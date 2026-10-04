import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserRouter } from "react-router-dom";
import { CreatePage } from "../src/pages/CreatePage";

describe("CreatePage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const renderComponent = () =>
    render(
      <BrowserRouter>
        <CreatePage />
      </BrowserRouter>
    );

  it("renders all four art styles and tones", () => {
    renderComponent();

    // Verify Art Styles
    expect(screen.getByText("Anime")).toBeInTheDocument();
    expect(screen.getByText("Pixel Art")).toBeInTheDocument();
    expect(screen.getByText("Comic Book")).toBeInTheDocument();
    expect(screen.getByText("Realistic")).toBeInTheDocument();

    // Verify Tones
    expect(screen.getByText("Light-hearted")).toBeInTheDocument();
    expect(screen.getByText("Dramatic")).toBeInTheDocument();
    expect(screen.getByText("Poetic")).toBeInTheDocument();
    expect(screen.getByText("Funny")).toBeInTheDocument();
  });

  it("shows custom setting input when Custom setting is selected", async () => {
    renderComponent();

    const settingSelect = screen.getByLabelText(/3\. Setting/i);
    fireEvent.change(settingSelect, { target: { value: "Custom setting" } });

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/A cyberpunk sunken ocean/i)).toBeInTheDocument();
    });
  });

  it("validates story prompt and displays error if too short", async () => {
    renderComponent();

    const promptInput = screen.getByLabelText(/1\. Story Concept/i);
    fireEvent.change(promptInput, { target: { value: "Too short" } });

    const submitBtn = screen.getByRole("button", { name: /Generate 5-Panel Comic/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Story prompt must be at least 10 characters/i)).toBeInTheDocument();
    });
  });
});
