/**
 * HTTP client for ComicCraft REST API.
 */

import type {
  ComicCreateRequest,
  ComicRegenerateRequest,
  ComicResponse,
  JobCreateResponse,
  PDFExportResponse,
} from "./types";

export interface HealthData {
  status: string;
  version: string;
  environment: string;
  storage_writable: boolean;
}

export async function fetchHealth(): Promise<HealthData> {
  const response = await fetch("/api/v1/health");
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

export async function createComic(payload: ComicCreateRequest): Promise<JobCreateResponse> {
  const response = await fetch("/api/v1/comics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.error?.message || `Failed to create comic: ${response.statusText}`;
    throw new Error(message);
  }

  return response.json();
}

export async function getComic(comicId: string): Promise<ComicResponse> {
  const response = await fetch(`/api/v1/comics/${comicId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.error?.message || `Failed to load comic: ${response.statusText}`;
    throw new Error(message);
  }
  return response.json();
}

export async function regenerateComic(
  comicId: string,
  payload: ComicRegenerateRequest
): Promise<JobCreateResponse> {
  const response = await fetch(`/api/v1/comics/${comicId}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.error?.message || `Failed to regenerate comic: ${response.statusText}`;
    throw new Error(message);
  }

  return response.json();
}

export async function exportComicPdf(comicId: string): Promise<PDFExportResponse> {
  const response = await fetch(`/api/v1/comics/${comicId}/export`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.error?.message || `Failed to export PDF: ${response.statusText}`;
    throw new Error(message);
  }

  return response.json();
}
