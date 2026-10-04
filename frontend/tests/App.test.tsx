import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../src/App";

describe("App Foundation", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders ComicCraft branding and headline", async () => {
    // Mock health API fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        version: "0.1.0",
        environment: "test",
        storage_writable: true,
      }),
    } as unknown as Response);

    render(<App />);

    expect(screen.getByText("COMICCRAFT")).toBeInTheDocument();
    expect(screen.getByText(/AI Comic Generator with/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/API v0.1.0 Connected/i)).toBeInTheDocument();
    });
  });

  it("displays error state when health API fails", async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error("Network Error"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/API Offline/i)).toBeInTheDocument();
    });
  });
});
