"""Professional PDF export generator using ReportLab."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus import (
    Image as PlatypusImage,
)

from app.core.config import settings
from app.core.errors import GenerationException
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFExporter:
    """Generates publication-grade multi-page PDFs for finished comics."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or settings.pdfs_storage_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(
        self,
        comic_id: str,
        title: str,
        character_name: str,
        setting: str,
        tone: str,
        art_style: str,
        synopsis: str,
        panels: list[dict[str, Any]],
        image_dir: Path,
    ) -> Path:
        """
        Compile complete comic into a 6-page PDF.
        Page 1: Title/cover page
        Pages 2-6: Individual panel pages
        """
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"comic_{comic_id}_{timestamp}.pdf"
        output_file = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "CoverTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=36,
            textColor=colors.HexColor("#4F46E5"),  # Indigo
            alignment=1,  # Center
            spaceAfter=15,
        )

        subtitle_style = ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#475569"),  # Slate-600
            alignment=1,
            spaceAfter=25,
        )

        metadata_label_style = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
        )

        metadata_val_style = ParagraphStyle(
            "MetaValue",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#334155"),
        )

        synopsis_style = ParagraphStyle(
            "CoverSynopsis",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#334155"),
            alignment=1,
            spaceBefore=15,
            spaceAfter=20,
        )

        panel_heading_style = ParagraphStyle(
            "PanelHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=4,
        )

        scene_desc_style = ParagraphStyle(
            "SceneDesc",
            parent=styles["Italic"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=8,
        )

        caption_style = ParagraphStyle(
            "CaptionBox",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#B45309"),  # Amber-700
            spaceAfter=6,
        )

        narration_style = ParagraphStyle(
            "NarrationText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1E293B"),
        )

        dialogue_text_style = ParagraphStyle(
            "DialogueText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#0F172A"),
        )

        story_elements: list[Flowable] = []

        # ======================================================================
        # PAGE 1: TITLE / COVER PAGE
        # ======================================================================
        story_elements.append(Spacer(1, 1.2 * inch))
        story_elements.append(
            Paragraph(
                "COMICCRAFT PRODUCTION",
                ParagraphStyle(
                    "Brand",
                    fontName="Helvetica-Bold",
                    fontSize=12,
                    leading=14,
                    textColor=colors.HexColor("#E11D48"),
                    alignment=1,
                    spaceAfter=10,
                ),
            )
        )
        story_elements.append(Paragraph(title, title_style))
        story_elements.append(Paragraph("An Illustrated Graphic Novel in 5 Panels", subtitle_style))
        story_elements.append(
            HRFlowable(width="60%", thickness=2, color=colors.HexColor("#CBD5E1"), spaceAfter=20)
        )

        # Metadata Table
        date_str = datetime.now(UTC).strftime("%B %d, %Y - %H:%M UTC")
        meta_data = [
            [
                Paragraph("Protagonist:", metadata_label_style),
                Paragraph(character_name, metadata_val_style),
            ],
            [Paragraph("Setting:", metadata_label_style), Paragraph(setting, metadata_val_style)],
            [
                Paragraph("Narrative Tone:", metadata_label_style),
                Paragraph(tone, metadata_val_style),
            ],
            [
                Paragraph("Visual Art Style:", metadata_label_style),
                Paragraph(art_style, metadata_val_style),
            ],
            [
                Paragraph("Generated On:", metadata_label_style),
                Paragraph(date_str, metadata_val_style),
            ],
        ]
        meta_table = Table(meta_data, colWidths=[2.0 * inch, 3.5 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        story_elements.append(meta_table)

        if synopsis:
            story_elements.append(Spacer(1, 20))
            story_elements.append(Paragraph(f'"{synopsis}"', synopsis_style))

        story_elements.append(Spacer(1, 1.0 * inch))
        story_elements.append(
            Paragraph(
                "ComicCraft AI Comic Platform &copy; 2026",
                ParagraphStyle(
                    "Footer",
                    fontName="Helvetica",
                    fontSize=9,
                    textColor=colors.HexColor("#94A3B8"),
                    alignment=1,
                ),
            )
        )
        story_elements.append(PageBreak())

        # ======================================================================
        # PAGES 2-6: PANEL PAGES (1 PANEL PER PAGE)
        # ======================================================================
        for idx, panel in enumerate(panels, start=1):
            p_num = panel.get("panel", idx)
            p_title = panel.get("title", f"Panel {p_num}")
            p_scene = panel.get("scene_description", "")
            p_caption = panel.get("caption", "")
            p_narration = panel.get("narration", "")
            p_dialogue = panel.get("dialogue", [])

            # Header
            story_elements.append(
                Paragraph(f"PANEL {p_num}: {p_title.upper()}", panel_heading_style)
            )
            if p_scene:
                story_elements.append(Paragraph(f"Scene: {p_scene}", scene_desc_style))

            # Artwork Image
            img_path = image_dir / f"panel_{p_num}.png"
            if img_path.exists():
                # Fit image within printable width and max height
                img_width = 7.0 * inch
                img_height = 4.2 * inch
                panel_img = PlatypusImage(str(img_path), width=img_width, height=img_height)
                story_elements.append(panel_img)
            else:
                # Decorative fallback box
                empty_box = Table(
                    [[Paragraph("Artwork in generation", styles["Normal"])]],
                    colWidths=[7.0 * inch],
                    rowHeights=[3.5 * inch],
                )
                empty_box.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ]
                    )
                )
                story_elements.append(empty_box)

            story_elements.append(Spacer(1, 10))

            # Caption Banner (if present)
            if p_caption:
                story_elements.append(
                    Table(
                        [[Paragraph(f"CAPTION: {p_caption}", caption_style)]],
                        colWidths=[7.0 * inch],
                        style=TableStyle(
                            [
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, -1),
                                    colors.HexColor("#FEF3C7"),
                                ),  # Amber-100
                                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCD34D")),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ]
                        ),
                    )
                )
                story_elements.append(Spacer(1, 6))

            # Narration Box
            if p_narration:
                story_elements.append(
                    Table(
                        [[Paragraph(f"<b>NARRATOR:</b> {p_narration}", narration_style)]],
                        colWidths=[7.0 * inch],
                        style=TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                                ("TOPPADDING", (0, 0), (-1, -1), 5),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ]
                        ),
                    )
                )
                story_elements.append(Spacer(1, 6))

            # Dialogue Callout Bubbles
            if p_dialogue:
                dialogue_rows = []
                for d in p_dialogue:
                    speaker = d.get("speaker", "Character")
                    text = d.get("text", "")
                    content = Paragraph(
                        f"<b>{speaker}:</b> &ldquo;{text}&rdquo;", dialogue_text_style
                    )
                    dialogue_rows.append([content])

                d_table = Table(dialogue_rows, colWidths=[7.0 * inch])
                d_table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, -1),
                                colors.HexColor("#EEF2FF"),
                            ),  # Indigo-50
                            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#C7D2FE")),
                            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E7FF")),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ]
                    )
                )
                story_elements.append(d_table)

            # Page break after every panel except the last
            if idx < len(panels):
                story_elements.append(PageBreak())

        try:
            doc.build(story_elements)
            logger.info(f"PDF successfully generated at: {output_file}")
            return output_file
        except Exception as exc:
            logger.exception(f"Failed to build PDF document: {exc}")
            raise GenerationException(
                f"PDF compilation failed: {exc}",
                code="PDF_GENERATION_FAILED",
            ) from exc


# Global exporter singleton
pdf_exporter = PDFExporter()
