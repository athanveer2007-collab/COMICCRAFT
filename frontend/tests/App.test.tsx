import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../src/App";

describe("App Shell & Routing", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders Navbar branding and Create Page on initial load", async () => {
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

    expect(screen.getAllByText("COMICCRAFT")[0]).toBeInTheDocument();
    expect(screen.getByText(/Create Your 5-Panel/i)).toBeInTheDocument();
    expect(screen.getByText(/Story Concept or Plot Idea/i)).toBeInTheDocument();
    expect(screen.getByText(/Main Character Name/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/API v0.1.0 Online/i)).toBeInTheDocument();
    });
  });
});
