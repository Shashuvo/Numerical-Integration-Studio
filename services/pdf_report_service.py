"""
Generates a professional PDF report of a calculation using ReportLab.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
)

from models.history_entry import MethodResultSnapshot
from models.integration_request import IntegrationRequest
from reports.report_templates import (
    PAGE_MARGIN,
    PLOT_IMAGE_HEIGHT,
    PLOT_IMAGE_WIDTH,
    build_comparison_table_style,
    build_report_styles,
)
from services.error_analysis_service import ErrorAnalysisService
from utils.constants import APP_NAME, METHOD_DISPLAY_NAMES
from utils.exceptions import ReportGenerationError
from utils.logger import get_logger

_COMPARISON_COLUMNS = (
    "Method",
    "Approximation",
    "Exact Value",
    "Absolute Error",
    "Relative Error",
    "Exec. Time (s)",
)


class PDFReportService:
    """Builds a complete PDF report: metadata, comparison table, and plots."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)
        self._error_analysis = ErrorAnalysisService()

    def generate(
        self,
        output_path: str | Path,
        request: IntegrationRequest,
        results: list[MethodResultSnapshot],
        exact_value: Optional[float],
        function_plot_image_path: Optional[str | Path] = None,
        convergence_plot_image_path: Optional[str | Path] = None,
    ) -> None:
        """Generate the PDF report and write it to ``output_path``.

        Args:
            output_path: Destination file path (parent dirs created if missing).
            request: The original computation request (function, limits, n).
            results: One snapshot per method that was computed.
            exact_value: The exact value if known, else None.
            function_plot_image_path: Path to a pre-rendered PNG of the
                function/approximation plot (e.g. saved via
                ``plots.function_plotter``), or None to omit it.
            convergence_plot_image_path: Path to a pre-rendered PNG of the
                convergence plot, or None to omit it.

        Raises:
            ReportGenerationError: If the PDF cannot be built or written.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        styles = build_report_styles()

        try:
            document = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                leftMargin=PAGE_MARGIN,
                rightMargin=PAGE_MARGIN,
                topMargin=PAGE_MARGIN,
                bottomMargin=PAGE_MARGIN,
                title=f"{APP_NAME} Report",
            )

            story = []
            story.extend(self._build_header(request, exact_value, styles))
            story.extend(self._build_comparison_section(results, styles))
            story.extend(
                self._build_plot_section(
                    "Function & Approximation", function_plot_image_path, styles
                )
            )
            story.extend(
                self._build_plot_section(
                    "Convergence Analysis", convergence_plot_image_path, styles
                )
            )

            document.build(story)
            self._logger.info("Generated PDF report at %s", output_path)
        except Exception as exc:  # noqa: BLE001 - ReportLab can raise many internal types
            self._logger.exception("Failed to generate PDF report")
            raise ReportGenerationError(f"Could not generate PDF report: {exc}") from exc

    def _build_header(
        self, request: IntegrationRequest, exact_value: Optional[float], styles
    ) -> list:
        """Build the title and metadata (date/function/limits/methods) section."""
        elements = [
            Paragraph(f"{APP_NAME}", styles["ReportTitle"]),
            Paragraph("Numerical Integration Calculation Report", styles["Heading3"]),
            Spacer(1, 12),
        ]

        method_names = ", ".join(METHOD_DISPLAY_NAMES.get(m, m) for m in request.methods)
        exact_text = f"{exact_value:.10f}" if exact_value is not None else "Not available (no closed form found)"

        # Superscripts/subscripts must use ReportLab's <super>/<sub> tags,
        # never Unicode glyphs, or they render as solid black boxes.
        function_display = request.function_expression.replace("^2", "<super>2</super>").replace(
            "^3", "<super>3</super>"
        )

        metadata_rows = [
            ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Function f(x):", function_display],
            ["Lower Limit (a):", f"{request.lower_limit}"],
            ["Upper Limit (b):", f"{request.upper_limit}"],
            ["Number of Intervals (n):", f"{request.num_intervals}"],
            ["Methods Used:", method_names],
            ["Exact Value:", exact_text],
        ]

        for label, value in metadata_rows:
            elements.append(
                Paragraph(f"<b>{label}</b> {value}", styles["Normal"])
            )
            elements.append(Spacer(1, 4))

        elements.append(Spacer(1, 10))
        return elements

    def _build_comparison_section(self, results: list[MethodResultSnapshot], styles) -> list:
        """Build the algorithm comparison table, with the best method highlighted."""
        elements = [Paragraph("Algorithm Comparison", styles["SectionHeading"])]

        if not results:
            elements.append(Paragraph("No results were computed.", styles["Normal"]))
            return elements

        table_data = [list(_COMPARISON_COLUMNS)]
        for result in results:
            display_name = METHOD_DISPLAY_NAMES.get(result.method_name, result.method_name)
            table_data.append(
                [
                    display_name,
                    f"{result.approximate_value:.8f}",
                    f"{result.exact_value:.8f}" if result.exact_value is not None else "N/A",
                    f"{result.absolute_error:.3e}" if result.absolute_error is not None else "N/A",
                    f"{result.relative_error:.3e}" if result.relative_error is not None else "N/A",
                    f"{result.execution_time_seconds:.6f}",
                ]
            )

        best_index = self._error_analysis.find_best_method_index(results)
        table_style = build_comparison_table_style(best_index, len(table_data))

        table = Table(table_data, hAlign="LEFT", repeatRows=1)
        table.setStyle(table_style)
        elements.append(table)

        if best_index is not None:
            best_name = METHOD_DISPLAY_NAMES.get(
                results[best_index].method_name, results[best_index].method_name
            )
            elements.append(Spacer(1, 6))
            elements.append(
                Paragraph(
                    f"<i>Most accurate method: {best_name} "
                    f"(lowest absolute error).</i>",
                    styles["Normal"],
                )
            )

        elements.append(Spacer(1, 10))
        return elements

    def _build_plot_section(
        self, heading: str, image_path: Optional[str | Path], styles
    ) -> list:
        """Build a section embedding a pre-rendered plot image, if provided."""
        elements = [Paragraph(heading, styles["SectionHeading"])]

        if image_path is None or not Path(image_path).exists():
            elements.append(
                Paragraph("No plot was generated for this section.", styles["Normal"])
            )
            return elements

        elements.append(
            Image(str(image_path), width=PLOT_IMAGE_WIDTH, height=PLOT_IMAGE_HEIGHT)
        )
        elements.append(Spacer(1, 10))
        return elements
