"""
Controller that drives PDF and CSV report generation for a computation outcome.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from models.comparison_model import ComputationOutcome
from plots.function_plotter import FunctionPlotter
from services.csv_export_service import CSVExportService
from services.pdf_report_service import PDFReportService
from views.widgets.plot_widget import PlotWidget
from utils.logger import get_logger


class ReportController:
    """Generates PDF/CSV reports from a ``ComputationOutcome``."""

    def __init__(self, pdf_service: PDFReportService, csv_service: CSVExportService) -> None:
        self._pdf_service = pdf_service
        self._csv_service = csv_service
        self._function_plotter = FunctionPlotter()
        self._logger = get_logger(__name__)

    def export_pdf(
        self,
        output_path: str | Path,
        outcome: ComputationOutcome,
        convergence_plot_image_path: Optional[str | Path] = None,
    ) -> None:
        """Render a fresh function plot and build the full PDF report.

        A dedicated off-screen ``PlotWidget`` is used to render the
        function plot for the report, rather than reusing the live GUI
        widget, so report generation never depends on what tab happens
        to be visible.

        Args:
            output_path: Destination PDF file path.
            outcome: The computation outcome to report on.
            convergence_plot_image_path: Optional path to a pre-rendered
                convergence plot image (if a convergence analysis was
                already run for this session).

        Raises:
            ReportGenerationError: If the PDF cannot be built or written.
        """
        temp_plot_widget = PlotWidget()
        self._function_plotter.plot(
            temp_plot_widget,
            outcome.function_model,
            outcome.request.lower_limit,
            outcome.request.upper_limit,
            outcome.raw_results,
        )

        temp_image_path = Path(output_path).with_suffix(".function_plot_temp.png")
        temp_plot_widget.figure.savefig(str(temp_image_path), dpi=130)

        try:
            self._pdf_service.generate(
                output_path,
                outcome.request,
                outcome.snapshots,
                outcome.exact_value,
                function_plot_image_path=temp_image_path,
                convergence_plot_image_path=convergence_plot_image_path,
            )
        finally:
            temp_image_path.unlink(missing_ok=True)

        self._logger.info("Exported PDF report to %s", output_path)

    def export_csv(self, output_path: str | Path, outcome: ComputationOutcome) -> None:
        """Export the computation outcome to CSV.

        Args:
            output_path: Destination CSV file path.
            outcome: The computation outcome to export.

        Raises:
            ReportGenerationError: If the CSV cannot be written.
        """
        self._csv_service.export(output_path, outcome.request, outcome.snapshots, outcome.exact_value)
        self._logger.info("Exported CSV report to %s", output_path)
