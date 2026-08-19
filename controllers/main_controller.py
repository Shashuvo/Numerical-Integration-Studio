"""
Top-level controller: wires ``MainWindow``'s signals to every service,
algorithm, and sub-controller in the application.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QFileDialog

from controllers.convergence_controller import ConvergenceController
from controllers.history_controller import HistoryController
from controllers.integration_controller import IntegrationController
from controllers.report_controller import ReportController
from database.db_manager import DatabaseManager
from models.comparison_model import ComputationOutcome
from models.integration_request import IntegrationRequest
from models.integration_result import IntegrationResult
from plots.convergence_plotter import ConvergencePlotter
from plots.function_plotter import FunctionPlotter
from services.convergence_service import ConvergenceService
from services.csv_export_service import CSVExportService
from services.error_analysis_service import ErrorAnalysisService
from services.expression_parser import ExpressionParserService
from services.pdf_report_service import PDFReportService
from services.theme_service import ThemeService
from utils.config_manager import ConfigManager
from utils.exceptions import NumericalIntegrationStudioError
from utils.logger import get_logger
from views.dialogs.history_dialog import HistoryDialog
from views.main_window import MainWindow


class MainController:
    """Connects every ``MainWindow`` signal to the appropriate service or
    sub-controller, and updates the view with each result.

    This is the only class in the application that imports from both
    ``views`` and ``services``/``algorithms``/``database`` — by design,
    per the MVC architecture: views emit signals, controllers coordinate,
    services/algorithms do the actual work.
    """

    def __init__(
        self,
        app: QApplication,
        window: MainWindow,
        config_manager: ConfigManager,
        database_manager: DatabaseManager,
        theme_service: ThemeService,
    ) -> None:
        self._app = app
        self._window = window
        self._config_manager = config_manager
        self._db = database_manager
        self._theme_service = theme_service
        self._logger = get_logger(__name__)

        # Services
        self._expression_parser = ExpressionParserService()
        self._error_analysis_service = ErrorAnalysisService()
        self._convergence_service = ConvergenceService()
        self._pdf_service = PDFReportService()
        self._csv_service = CSVExportService()

        # Plotters
        self._function_plotter = FunctionPlotter()
        self._convergence_plotter = ConvergencePlotter()

        # Sub-controllers
        self._integration_controller = IntegrationController(
            self._expression_parser, self._error_analysis_service
        )
        self._history_controller = HistoryController(self._db)
        self._report_controller = ReportController(self._pdf_service, self._csv_service)
        self._convergence_controller = ConvergenceController(
            self._convergence_service, self._convergence_plotter
        )

        # State: the most recently completed computation, used by
        # export/compare/convergence actions that operate on "the current result".
        self._last_outcome: Optional[ComputationOutcome] = None
        self._last_convergence_image_path: Optional[Path] = None

        self._connect_signals()
        self._window.function_input_widget.intervals_spin.setValue(
            self._config_manager.get("default_intervals", 100)
        )

    def _connect_signals(self) -> None:
        self._window.compute_requested.connect(self._on_compute_requested)
        self._window.new_requested.connect(self._on_new_requested)
        self._window.history_requested.connect(self._on_history_requested)
        self._window.export_pdf_requested.connect(self._on_export_pdf_requested)
        self._window.export_csv_requested.connect(self._on_export_csv_requested)
        self._window.theme_change_requested.connect(self._on_theme_change_requested)
        self._window.settings_saved.connect(self._on_settings_saved)
        self._window.compare_algorithms_requested.connect(self._on_compare_requested)
        self._window.convergence_analysis_requested.connect(self._on_convergence_requested)

    # ------------------------------------------------------------------ #
    # Compute
    # ------------------------------------------------------------------ #
    def _on_compute_requested(
        self, function_text: str, lower: float, upper: float, intervals: int, methods: list[str]
    ) -> None:
        self._window.show_busy(True)
        self._window.set_status_message("Computing...")

        try:
            request = IntegrationRequest(function_text, lower, upper, intervals, methods)
            outcome = self._integration_controller.compute(request)
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("Calculation Error", str(exc))
            self._window.set_status_message("Calculation failed.")
            return
        finally:
            self._window.show_busy(False)

        self._last_outcome = outcome
        self._last_convergence_image_path = None  # invalidated by a new computation

        self._window.display_results(outcome.snapshots)
        self._window.display_comparison(outcome.snapshots)
        self._function_plotter.plot(
            self._window.plot_widget, outcome.function_model, lower, upper, outcome.raw_results
        )
        self._window.plot_widget.apply_theme_colors(self._theme_service.current_theme == "dark")

        try:
            self._history_controller.save(outcome)
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("History Save Failed", str(exc))

        self._window.set_status_message(
            f"Computed {len(methods)} method(s) for f(x) = {function_text}."
        )

    def _on_new_requested(self) -> None:
        self._window.function_input_widget.function_edit.clear()
        self._window.function_input_widget.lower_limit_spin.setValue(0.0)
        self._window.function_input_widget.upper_limit_spin.setValue(1.0)
        self._window.function_input_widget.intervals_spin.setValue(
            self._config_manager.get("default_intervals", 100)
        )
        self._window.function_input_widget.clear_error()
        self._window.results_table_widget.clear_results()
        self._window.comparison_widget.clear_comparison()
        self._window.plot_widget.clear()
        self._window.convergence_plot_widget.clear()
        self._last_outcome = None
        self._last_convergence_image_path = None
        self._window.set_status_message("Ready")

    # ------------------------------------------------------------------ #
    # History
    # ------------------------------------------------------------------ #
    def _on_history_requested(self) -> None:
        try:
            entries = self._history_controller.fetch_all()
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("History Load Failed", str(exc))
            return

        # The dialog is created here (rather than via MainWindow) so that
        # a delete can refresh the same open dialog instance immediately -
        # a signal round-tripped through MainWindow would have no way to
        # reach back into the already-open modal dialog.
        dialog = HistoryDialog(entries, self._window)
        dialog.entry_selected.connect(lambda entry_id: self._on_history_entry_opened(entry_id, dialog))
        dialog.entry_delete_requested.connect(
            lambda entry_id: self._on_history_entry_deleted(entry_id, dialog)
        )
        dialog.exec()

    def _on_history_entry_opened(self, entry_id: int, dialog: HistoryDialog) -> None:
        entry = self._history_controller.fetch_by_id(entry_id)
        if entry is None:
            return

        self._window.function_input_widget.function_edit.setText(entry.function_expression)
        self._window.function_input_widget.lower_limit_spin.setValue(entry.lower_limit)
        self._window.function_input_widget.upper_limit_spin.setValue(entry.upper_limit)
        self._window.function_input_widget.intervals_spin.setValue(entry.num_intervals)
        self._window.method_selector_widget.set_selected_methods(entry.methods)
        self._window.display_results(entry.results)
        self._window.display_comparison(entry.results)

        try:
            function_model = self._expression_parser.parse(entry.function_expression)
            raw_results_for_plot = [
                IntegrationResult(
                    method_name=snapshot.method_name,
                    approximate_value=snapshot.approximate_value,
                    execution_time_seconds=snapshot.execution_time_seconds,
                    lower_limit=entry.lower_limit,
                    upper_limit=entry.upper_limit,
                    num_intervals=entry.num_intervals,
                )
                for snapshot in entry.results
            ]
            self._function_plotter.plot(
                self._window.plot_widget, function_model, entry.lower_limit, entry.upper_limit,
                raw_results_for_plot,
            )
            self._last_outcome = ComputationOutcome(
                function_model=function_model,
                request=IntegrationRequest(
                    entry.function_expression, entry.lower_limit, entry.upper_limit,
                    entry.num_intervals, entry.methods,
                ),
                raw_results=raw_results_for_plot,
                snapshots=entry.results,
                exact_value=entry.exact_value,
            )
        except NumericalIntegrationStudioError as exc:
            self._logger.warning("Could not replot reopened history entry: %s", exc)

        self._window.set_status_message(
            f"Loaded calculation from {entry.timestamp.strftime('%Y-%m-%d %H:%M')}."
        )
        dialog.accept()

    def _on_history_entry_deleted(self, entry_id: int, dialog: HistoryDialog) -> None:
        try:
            self._history_controller.delete(entry_id)
            updated_entries = self._history_controller.fetch_all()
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("Delete Failed", str(exc))
            return
        dialog.refresh(updated_entries)

    # ------------------------------------------------------------------ #
    # Reports
    # ------------------------------------------------------------------ #
    def _on_export_pdf_requested(self) -> None:
        if self._last_outcome is None:
            self._window.display_error(
                "No Results", "Please run a calculation before exporting a report."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._window, "Export PDF Report", "calculation_report.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        try:
            self._report_controller.export_pdf(
                file_path, self._last_outcome, self._last_convergence_image_path
            )
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("Export Failed", str(exc))
            return

        self._window.set_status_message(f"PDF report saved to {file_path}")

    def _on_export_csv_requested(self) -> None:
        if self._last_outcome is None:
            self._window.display_error(
                "No Results", "Please run a calculation before exporting a report."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._window, "Export CSV Report", "calculation_report.csv", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            self._report_controller.export_csv(file_path, self._last_outcome)
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("Export Failed", str(exc))
            return

        self._window.set_status_message(f"CSV report saved to {file_path}")

    # ------------------------------------------------------------------ #
    # Theme & Settings
    # ------------------------------------------------------------------ #
    def _on_theme_change_requested(self, theme_name: str) -> None:
        self._theme_service.apply_theme(self._app, theme_name)
        self._config_manager.set("theme", theme_name)
        is_dark = theme_name == "dark"
        self._window.plot_widget.apply_theme_colors(is_dark)
        self._window.convergence_plot_widget.apply_theme_colors(is_dark)
        self._window.set_status_message(f"Switched to {theme_name} theme.")

    def _on_settings_saved(self, settings: dict) -> None:
        self._config_manager.update(settings)
        if settings.get("theme") and settings["theme"] != self._theme_service.current_theme:
            self._on_theme_change_requested(settings["theme"])
        self._window.set_status_message("Settings saved.")

    # ------------------------------------------------------------------ #
    # Analysis
    # ------------------------------------------------------------------ #
    def _on_compare_requested(self) -> None:
        if self._last_outcome is None:
            self._window.display_error(
                "No Results", "Please run a calculation before comparing algorithms."
            )
            return
        self._window.tab_widget.setCurrentWidget(self._window.comparison_widget)

    def _on_convergence_requested(self) -> None:
        function_text = self._window.function_input_widget.get_function_text()
        lower = self._window.function_input_widget.get_lower_limit()
        upper = self._window.function_input_widget.get_upper_limit()
        intervals = self._window.function_input_widget.get_num_intervals()
        methods = self._window.method_selector_widget.selected_methods()

        if not function_text:
            self._window.display_error("No Function", "Please enter a function first.")
            return
        if not methods:
            self._window.display_error("No Method Selected", "Please select at least one method.")
            return

        try:
            function_model = self._expression_parser.parse(function_text)
        except NumericalIntegrationStudioError as exc:
            self._window.display_error("Invalid Function", str(exc))
            return

        self._window.set_status_message("Running convergence analysis...")
        self._convergence_controller.run_and_plot(
            self._window.convergence_plot_widget, function_model, lower, upper, methods, intervals
        )
        self._window.convergence_plot_widget.apply_theme_colors(
            self._theme_service.current_theme == "dark"
        )
        self._window.tab_widget.setCurrentWidget(self._window.convergence_plot_widget)

        # Cache a PNG of the convergence plot so a subsequent PDF export
        # (Module 8) can embed it without re-running the sweep.
        temp_path = Path(tempfile.gettempdir()) / "nis_convergence_plot_cache.png"
        self._window.convergence_plot_widget.figure.savefig(str(temp_path), dpi=130)
        self._last_convergence_image_path = temp_path

        self._window.set_status_message(f"Convergence analysis complete for {len(methods)} method(s).")
