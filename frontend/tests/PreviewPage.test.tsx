import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { PreviewPage } from "../src/pages/PreviewPage";

const mockComic = {
  id: "test-comic-preview",
  prompt: "A brave fox exploring an enchanted forest",
  character_name: "Free",
  setting: "Forest",
  tone: "Dramatic",
  art_style: "Anime",
  title: "Chronicles of the Whisperwood",
  synopsis: "A journey of courage and starlight.",
  status: "completed",
  character_sheet: {
    name: "Free",
    appearance: "Sleek red fox",
    age_presentation: "Young adult",
    hair: "Russet fur",
    face: "Pointed ears",
    eyes: "Amber",
    outfit: "Green cloak",
    primary_colors: ["Orange", "Green"],
    accessories: ["Leaf clasp"],
    distinctive_features: ["Ear notch"],
  },
  panels: [
    {
      panel: 1,
      title: "The Silent Forest",
      scene_description: "Free arrives at the border of the forest.",
      caption: "The forest waits in emerald silence.",
      narration: "Free paused beneath the canopy.",
      dialogue: [{ speaker: "Free", text: "The stars guided me here." }],
      image_prompt: "Free the fox in anime style",
      image_url: "/storage/images/test/panel_1.png",
    },
    {
      panel: 2,
      title: "The Glowing Track",
      scene_description: "Free spots glowing footprints.",
      caption: "A trail of starlight.",
      narration: "The path was clear.",
      dialogue: [{ speaker: "Free", text: "Footsteps..." }],
      image_prompt: "Glowing footsteps on moss",
      image_url: "/storage/images/test/panel_2.png",
    },
  ],
};

describe("PreviewPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches and renders comic title, character tags, and panel cards", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockComic,
    } as unknown as Response);

    render(
      <MemoryRouter initialEntries={["/comics/test-comic-preview"]}>
        <Routes>
          <Route path="/comics/:id" element={<PreviewPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Chronicles of the Whisperwood")).toBeInTheDocument();
      expect(screen.getByText("The Silent Forest")).toBeInTheDocument();
      expect(screen.getByText(/The stars guided me here/i)).toBeInTheDocument();
    });

    expect(screen.getByText("Anime")).toBeInTheDocument();
    expect(screen.getByText("Dramatic")).toBeInTheDocument();
  });

  it("opens regenerate modal when Regenerate button is clicked", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockComic,
    } as unknown as Response);

    render(
      <MemoryRouter initialEntries={["/comics/test-comic-preview"]}>
        <Routes>
          <Route path="/comics/:id" element={<PreviewPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Chronicles of the Whisperwood")).toBeInTheDocument();
    });

    const regenBtn = screen.getByRole("button", { name: /Regenerate Style\/Tone/i });
    fireEvent.click(regenBtn);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText(/Choose a different tone and art style/i)).toBeInTheDocument();
  });
});
