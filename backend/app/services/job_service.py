"""Pub/Sub event broadcaster for Server-Sent Events (SSE)."""

import asyncio
from collections.abc import AsyncGenerator

from app.core.logging import get_logger
from app.schemas.events import ComicEvent

logger = get_logger(__name__)


class EventBroadcaster:
    """Manages SSE subscribers and broadcasts generation events in real time."""

    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[ComicEvent]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, comic_id: str) -> AsyncGenerator[str, None]:
        """Subscribe to events for a specific comic. Yields SSE-formatted strings."""
        queue: asyncio.Queue[ComicEvent] = asyncio.Queue(maxsize=100)
        async with self._lock:
            if comic_id not in self._subscribers:
                self._subscribers[comic_id] = set()
            self._subscribers[comic_id].add(queue)

        logger.info(f"New SSE subscriber attached to comic [{comic_id}]")
        try:
            while True:
                event = await queue.get()
                yield event.to_sse()
                if event.stage in ("ready", "failed"):
                    break
        except asyncio.CancelledError:
            logger.info(f"SSE client disconnected from comic [{comic_id}]")
        finally:
            async with self._lock:
                if comic_id in self._subscribers:
                    self._subscribers[comic_id].discard(queue)
                    if not self._subscribers[comic_id]:
                        del self._subscribers[comic_id]

    async def broadcast(self, comic_id: str, event: ComicEvent) -> None:
        """Broadcast an event to all subscribers listening to the given comic."""
        async with self._lock:
            listeners = self._subscribers.get(comic_id, set()).copy()

        logger.info(
            f"Broadcasting event [{event.stage}] ({event.progress}%) to {len(listeners)} listeners on comic [{comic_id}]"
        )
        for queue in listeners:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(
                    f"Subscriber queue full for comic [{comic_id}], dropping event [{event.stage}]"
                )


# Global event broadcaster singleton
broadcaster = EventBroadcaster()
