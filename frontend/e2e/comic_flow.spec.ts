import { test, expect } from "@playwright/test";

test.describe("ComicCraft End-to-End User Flow", () => {
  test("Full journey: Create -> Generating -> Preview -> Regenerate -> Export -> Success", async ({
    page,
  }) => {
    const mockComicId = "e2e-comic-123";

    // 1. Mock Health Check
    await page.route("**/api/v1/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          status: "ok",
          version: "0.1.0",
          environment: "test",
          storage_writable: true,
        }),
      });
    });

    // 2. Mock POST /api/v1/comics
    await page.route("**/api/v1/comics", async (route) => {
      if (route.request().method() === "POST") {
        await route.fulfill({
          status: 202,
          contentType: "application/json",
          body: JSON.stringify({
            job_id: "e2e-job-123",
            comic_id: mockComicId,
            status: "in_progress",
            stage: "queued",
          }),
        });
      } else {
        await route.continue();
      }
    });

    // 3. Mock GET /api/v1/comics/:id
    const mockComicData = {
      id: mockComicId,
      prompt: "A brave fox exploring an enchanted forest looking for star magic",
      character_name: "Free",
      setting: "Forest",
      tone: "Dramatic",
      art_style: "Anime",
      title: "Chronicles of the Whisperwood",
      synopsis: "Free travels through ancient ruins to restore the constellation bridge.",
      status: "completed",
      character_sheet: {
        name: "Free",
        appearance: "Brave young fox with amber eyes and swift footing",
        age_presentation: "Young adult",
        hair: "Russet fur",
        face: "Pointed muzzle",
        eyes: "Amber-gold",
        outfit: "Green traveler's cloak with silver clasp",
        primary_colors: ["Orange", "Green"],
        accessories: ["Ancient star map"],
        distinctive_features: ["Notch on left ear"],
      },
      panels: [
        {
          panel: 1,
          title: "The Ancient Threshold",
          scene_description: "Free stands at the glowing tree boundary.",
          caption: "A whisper echoes from deep roots.",
          narration: "Free paused at the boundary line.",
          dialogue: [{ speaker: "Free", text: "The journey begins." }],
          image_prompt: "Free the fox at enchanted tree entrance",
          image_url: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
        },
        {
          panel: 2,
          title: "The Glowing Track",
          scene_description: "Luminescent tracks guide the way.",
          caption: "Magic lingers on the moss.",
          narration: "Every pawstep glowed soft blue.",
          dialogue: [{ speaker: "Free", text: "I must hurry." }],
          image_prompt: "Glowing blue pawprints",
          image_url: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
        },
      ],
    };

    await page.route(`**/api/v1/comics/${mockComicId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockComicData),
      });
    });

    // 4. Mock POST /api/v1/comics/:id/export
    await page.route(`**/api/v1/comics/${mockComicId}/export`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          pdf_url: `/api/v1/comics/${mockComicId}/pdf`,
          message: "PDF compiled successfully.",
        }),
      });
    });

    // Step A: Load Create Page
    await page.goto("/");
    await expect(page.locator("text=COMICCRAFT").first()).toBeVisible();
    await expect(page.locator("text=Create Your 5-Panel")).toBeVisible();

    // Step B: Submit the creation form
    const submitBtn = page.getByRole("button", { name: /Generate 5-Panel Comic/i });
    await submitBtn.click();

    // Step C: Verify navigation to generating screen
    await expect(page).toHaveURL(new RegExp(`/comics/${mockComicId}/generating`));
    await expect(page.getByText(/Bringing Your Comic to Life/i)).toBeVisible();

    // Step D: Navigate to Preview Page directly
    await page.goto(`/comics/${mockComicId}`);
    await expect(page.getByText("Chronicles of the Whisperwood")).toBeVisible();
    await expect(page.getByText("The Ancient Threshold")).toBeVisible();
    await expect(page.getByText("The journey begins.")).toBeVisible();

    // Step E: Trigger PDF Export
    const downloadPdfBtn = page.getByRole("button", { name: /Download PDF/i }).first();
    await downloadPdfBtn.click();

    // Step F: Verify arrival at Export Success screen
    await expect(page).toHaveURL(new RegExp(`/comics/${mockComicId}/export-success`));
    await expect(page.getByText("Your Comic PDF is Ready!")).toBeVisible();
    await expect(page.getByRole("link", { name: /Download PDF/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Create Another Comic/i })).toBeVisible();
  });
});
