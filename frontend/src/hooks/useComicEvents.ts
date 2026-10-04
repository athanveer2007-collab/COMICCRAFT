/**
 * Custom React hook subscribing to real-time Server-Sent Events (SSE) for comic generation.
 */

import { useEffect, useState, useRef } from "react";
import type { ComicEvent, PanelResponse } from "@/api/types";

export interface UseComicEventsReturn {
  stage: string;
  progress: number;
  message: string;
  panels: Record<number, PanelResponse>;
  isCompleted: boolean;
  isFailed: boolean;
  error: string | null;
}

export function useComicEvents(comicId: string | undefined): UseComicEventsReturn {
  const [stage, setStage] = useState<string>("queued");
  const [progress, setProgress] = useState<number>(0);
  const [message, setMessage] = useState<string>("Initializing generation queue...");
  const [panels, setPanels] = useState<Record<number, PanelResponse>>({});
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [isFailed, setIsFailed] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!comicId) return;

    const sseUrl = `/api/v1/comics/${comicId}/events`;
    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    const handleEvent = (e: MessageEvent) => {
      try {
        const payload: ComicEvent = JSON.parse(e.data);
        setStage(payload.stage);
        setProgress(payload.progress);
        setMessage(payload.message);

        if (payload.panel_index && payload.panel_data) {
          setPanels((prev) => ({
            ...prev,
            [payload.panel_index as number]: payload.panel_data as PanelResponse,
          }));
        }

        if (payload.stage === "ready") {
          setIsCompleted(true);
          es.close();
        } else if (payload.stage === "failed") {
          setIsFailed(true);
          setError(payload.error || "Generation pipeline failed.");
          es.close();
        }
      } catch (err) {
        console.error("Failed to parse SSE event data:", err);
      }
    };

    // Generic and specific stage listeners
    es.onmessage = handleEvent;
    const stages = [
      "queued",
      "outline",
      "story",
      "images",
      "image_panel_1",
      "image_panel_2",
      "image_panel_3",
      "image_panel_4",
      "image_panel_5",
      "layout",
      "ready",
      "failed",
    ];

    stages.forEach((st) => {
      es.addEventListener(st, handleEvent);
    });

    es.onerror = () => {
      // If error before completion, mark warning or handle retry
      if (!isCompleted && !isFailed) {
        setMessage("Reconnecting event stream...");
      }
    };

    return () => {
      es.close();
    };
  }, [comicId, isCompleted, isFailed]);

  return {
    stage,
    progress,
    message,
    panels,
    isCompleted,
    isFailed,
    error,
  };
}
