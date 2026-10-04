"""Style system, tone presets, and prompt engineering templates."""

from dataclasses import dataclass

from app.ai.schemas import CharacterSheet


@dataclass(frozen=True)
class ArtStylePreset:
    """Preset configuration for visual art rendering."""

    name: str
    display_name: str
    positive_prompt_fragment: str
    negative_prompt: str
    visual_characteristics: str
    rendering_guidance: str


@dataclass(frozen=True)
class TonePreset:
    """Preset configuration for narrative tone and pacing."""

    name: str
    display_name: str
    narrative_characteristics: str
    dialogue_characteristics: str
    visual_mood: str


# Global Negative Prompt Anchor against typical AI generation artifacts
COMMON_NEGATIVE_PROMPTS = (
    "text, watermark, typography, signature, subtitles, speech bubbles, logo, "
    "blurry, bad anatomy, bad hands, missing fingers, extra limbs, floating limbs, "
    "disconnected limbs, mutated hands, poorly drawn face, deformed eyes, "
    "duplicate characters, inconsistent clothing, morbid, mutilated, low quality, worst quality"
)

# Supported Art Styles
ART_STYLE_PRESETS: dict[str, ArtStylePreset] = {
    "Anime": ArtStylePreset(
        name="Anime",
        display_name="Anime",
        positive_prompt_fragment=(
            "vibrant anime aesthetic, high-quality Japanese animation still, crisp lineart, "
            "cel shading, dynamic composition, dramatic atmospheric lighting, Makoto Shinkai inspired scenery"
        ),
        negative_prompt=f"{COMMON_NEGATIVE_PROMPTS}, 3d render, photorealistic, western comic",
        visual_characteristics="Expressive anime eyes, sharp hair highlights, lush painted backgrounds, vivid lighting.",
        rendering_guidance="Focus on emotive character expressions and cinematic framing with vibrant color grading.",
    ),
    "Pixel Art": ArtStylePreset(
        name="Pixel Art",
        display_name="Pixel Art",
        positive_prompt_fragment=(
            "masterpiece 16-bit pixel art style, detailed sprite artwork, clean pixel clusters, "
            "nostalgic retro game aesthetic, sharp edges, carefully selected color palette"
        ),
        negative_prompt=f"{COMMON_NEGATIVE_PROMPTS}, smooth gradients, anti-aliased blur, 3d render, photographic",
        visual_characteristics="Distinct pixel grid, retro palette, high readability of shapes and silhouette.",
        rendering_guidance="Preserve authentic pixel aesthetic without blurred digital smoothing or photographic noise.",
    ),
    "Comic Book": ArtStylePreset(
        name="Comic Book",
        display_name="Comic Book",
        positive_prompt_fragment=(
            "classic American graphic novel comic book style, bold ink contours, Ben-Day dot halftone shading, "
            "striking dramatic shadows, dynamic superhero comic panel composition, pulp illustration"
        ),
        negative_prompt=f"{COMMON_NEGATIVE_PROMPTS}, photographic, soft airbrush, 3d cgi render",
        visual_characteristics="Heavy black ink cross-hatching, halftone dots, high contrast chiaroscuro, punchy primary accents.",
        rendering_guidance="Use angular shadows, heroic perspective, and dynamic visual tension.",
    ),
    "Realistic": ArtStylePreset(
        name="Realistic",
        display_name="Realistic",
        positive_prompt_fragment=(
            "cinematic live-action film still, 35mm photograph, natural atmospheric lighting, "
            "photorealistic textures, realistic skin and hair fidelity, shallow depth of field"
        ),
        negative_prompt=f"{COMMON_NEGATIVE_PROMPTS}, cartoon, anime, illustration, drawing, painting, stylized, lowres",
        visual_characteristics="True-to-life physics, believable lighting falloff, rich tactile textures, cinematic color palette.",
        rendering_guidance="Capture genuine depth, natural focal bokeh, and nuanced authentic lighting.",
    ),
}

# Supported Narrative Tones
TONE_PRESETS: dict[str, TonePreset] = {
    "Light-hearted": TonePreset(
        name="Light-hearted",
        display_name="Light-hearted",
        narrative_characteristics="Uplifting, optimistic, breezy pacing with warm discoveries and gentle resolution.",
        dialogue_characteristics="Casual, friendly, cheerful banter with positive word choices.",
        visual_mood="Bright golden daylight, soft ambient pastel hues, warm sunbeams.",
    ),
    "Dramatic": TonePreset(
        name="Dramatic",
        display_name="Dramatic",
        narrative_characteristics="High stakes, escalating tension, intense emotional beats, powerful climax.",
        dialogue_characteristics="Weighty, earnest, urgent, impactful phrasing.",
        visual_mood="High contrast shadows, moody atmospheric haze, intense color contrasts, stormy or brooding ambience.",
    ),
    "Poetic": TonePreset(
        name="Poetic",
        display_name="Poetic",
        narrative_characteristics="Lyrical, contemplative, introspective pacing emphasizing symbolism and resonance.",
        dialogue_characteristics="Metaphorical, gentle, reflective cadence.",
        visual_mood="Ethereal twilight, mist, glowing particles, dreamy dusk lighting.",
    ),
    "Funny": TonePreset(
        name="Funny",
        display_name="Funny",
        narrative_characteristics="Playful situations, comedic misunderstandings, slapstick timing, punchy twist.",
        dialogue_characteristics="Witty, ironic, punchy, humorous one-liners.",
        visual_mood="Exaggerated angles, vibrant popping colors, animated expressions.",
    ),
}

SUPPORTED_SETTINGS: list[str] = ["School", "Forest", "Space", "City", "Custom setting"]


def get_art_style(name: str) -> ArtStylePreset:
    """Retrieve art style preset or default to Anime."""
    return ART_STYLE_PRESETS.get(name, ART_STYLE_PRESETS["Anime"])


def get_tone(name: str) -> TonePreset:
    """Retrieve tone preset or default to Dramatic."""
    return TONE_PRESETS.get(name, TONE_PRESETS["Dramatic"])


def build_character_sheet_prompt(
    character_name: str,
    story_prompt: str,
    setting: str,
    art_style: str,
) -> str:
    """Build prompt for generating canonical character sheet."""
    style_preset = get_art_style(art_style)
    return f"""You are a master character designer for comics and graphic novels.
Create a detailed, canonical Character Sheet for the main character '{character_name}' based on the story idea below.

Story Idea: {story_prompt}
Setting: {setting}
Art Style: {style_preset.display_name} ({style_preset.visual_characteristics})

Guidelines:
1. Define clear, memorable visual attributes that make this character instantly recognizable across 5 comic panels.
2. Specify exact colors (e.g. 'crimson scarf', 'emerald eyes'), distinct silhouette, and key accessories.
3. Keep the description visual and actionable for image generation.
"""


def build_comic_script_prompt(
    story_prompt: str,
    character_sheet: CharacterSheet,
    setting: str,
    tone: str,
    art_style: str,
    custom_setting: str | None = None,
) -> str:
    """Build prompt for generating a complete 5-panel comic script with image generation prompts."""
    resolved_setting = (
        custom_setting if setting.lower() == "custom setting" and custom_setting else setting
    )
    style_preset = get_art_style(art_style)
    tone_preset = get_tone(tone)
    char_summary = character_sheet.to_prompt_summary()

    return f"""You are a professional comic book writer and visual director.
Create a complete, coherent, exactly 5-PANEL comic strip based on the premise and character below.

PREMISE: {story_prompt}
SETTING: {resolved_setting}
TONE: {tone_preset.display_name} — {tone_preset.narrative_characteristics} (Dialogue: {tone_preset.dialogue_characteristics})
VISUAL ART STYLE: {style_preset.display_name} ({style_preset.positive_prompt_fragment})
CANONICAL CHARACTER IDENTITY:
{char_summary}

STORY STRUCTURE REQUIREMENTS (Strict 5-Panel Arc):
- Panel 1: Establishing Beat / Inciting Incident. Establish the character in the setting.
- Panel 2: Progressive Action / Rising Complication. The character encounters an obstacle or curiosity.
- Panel 3: Rising Tension / Discovery. A turning point or major revelation unfolds.
- Panel 4: Climax / Decisive Moment. The peak emotional or action-packed beat.
- Panel 5: Resolution / Aftermath / Punchline. The closing beat, reflecting the chosen tone.

IMAGE PROMPT RULES FOR EVERY PANEL:
1. The `image_prompt` MUST explicitly include the key visual traits of {character_sheet.name} ({character_sheet.outfit}, {character_sheet.hair}, {", ".join(character_sheet.primary_colors)}) so the character remains completely recognizable.
2. The `image_prompt` MUST include camera framing (e.g., 'wide shot', 'dramatic close-up', 'medium low-angle shot') and the lighting mood ({tone_preset.visual_mood}).
3. Append style anchors: "{style_preset.positive_prompt_fragment}".
4. Do NOT request text, speech bubbles, or captions inside the `image_prompt`—the text will be laid out by the application.
"""
