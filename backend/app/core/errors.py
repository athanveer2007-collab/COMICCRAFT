"""Custom exceptions and centralized error handlers."""

import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_ctx_var

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{resource_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationException(AppException):
    """Business validation failure."""

    def __init__(self, message: str) -> None:
        super().__init__(
            code="VALIDATION_FAILED",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class GenerationException(AppException):
    """AI Generation failure."""

    def __init__(self, message: str, code: str = "GENERATION_FAILED") -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def register_error_handlers(app: FastAPI) -> None:
    """Register uniform exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = request_id_ctx_var.get() or str(uuid.uuid4())
        logger.warning(
            f"Handled application exception: {exc.code} - {exc.message}",
            extra={"code": exc.code, "request_id": req_id},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = request_id_ctx_var.get() or str(uuid.uuid4())
        logger.info(
            f"Validation error: {exc.errors()}",
            extra={"request_id": req_id},
        )
        # Summarize validation errors into human-readable text
        error_msgs = []
        for err in exc.errors():
            loc = " -> ".join(str(item) for item in err.get("loc", []))
            msg = err.get("msg", "Invalid value")
            error_msgs.append(f"{loc}: {msg}")
        summary_msg = "; ".join(error_msgs) if error_msgs else "Invalid request payload."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": summary_msg,
                    "request_id": req_id,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        req_id = request_id_ctx_var.get() or str(uuid.uuid4())
        code_map = {
            404: "NOT_FOUND",
            403: "FORBIDDEN",
            401: "UNAUTHORIZED",
            405: "METHOD_NOT_ALLOWED",
            429: "RATE_LIMITED",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "request_id": req_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = request_id_ctx_var.get() or str(uuid.uuid4())
        logger.exception(
            f"Unhandled server error: {str(exc)}",
            extra={"request_id": req_id},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "request_id": req_id,
                }
            },
        )
