"""
Shared ReportLab styling and layout helpers for PDF report generation.

Kept separate from ``pdf_report_service.py`` so visual styling (colors,
fonts, table formatting) can be tuned in one place without touching the
report-assembly logic.
"""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle

BRAND_COLOR = colors.HexColor("#4C5B8C")
BEST_ROW_COLOR = colors.HexColor("#D9F2E1")
HEADER_BG_COLOR = colors.HexColor("#EDEFF7")
GRID_COLOR = colors.HexColor("#D9DCE3")

PAGE_MARGIN = 0.6 * inch
PLOT_IMAGE_WIDTH = 6.5 * inch
PLOT_IMAGE_HEIGHT = 3.6 * inch


def build_report_styles() -> StyleSheet1:
    """Build the paragraph style sheet used throughout the PDF report.

    Returns:
        A ReportLab ``StyleSheet1`` with the base styles plus custom
        "ReportTitle", "SectionHeading", and "MetaLabel" styles added.
    """
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            textColor=BRAND_COLOR,
            fontSize=20,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            textColor=BRAND_COLOR,
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
        )
    )
    return styles


def build_comparison_table_style(best_row_index: int | None, num_rows: int) -> TableStyle:
    """Build the ``TableStyle`` for the method comparison table.

    Args:
        best_row_index: The 0-based data-row index (excluding the header)
            of the most accurate method, or None if no row should be
            highlighted. Note: +1 is added internally to account for
            the header row occupying row 0 of the table.
        num_rows: Total number of rows in the table, including the header.

    Returns:
        A ``TableStyle`` with header formatting, grid lines, and (if
        applicable) a highlighted best-performing row.
    """
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HEADER_BG_COLOR]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    if best_row_index is not None:
        table_row = best_row_index + 1  # +1 for header row
        if 0 < table_row < num_rows:
            style_commands.append(("BACKGROUND", (0, table_row), (-1, table_row), BEST_ROW_COLOR))
            style_commands.append(("FONTNAME", (0, table_row), (-1, table_row), "Helvetica-Bold"))

    return TableStyle(style_commands)
