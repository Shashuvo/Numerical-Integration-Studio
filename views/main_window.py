"""
The application's main window: menu bar, toolbar, status bar, sidebar
control panel, and a tabbed results area.

Following MVC, this class only builds UI and emits signals describing
user intent (compute requested, export requested, theme changed, etc.).
It never calls algorithms, services, or the database directly — a
controller (wired in ``controllers/main_controller.py``) subscribes to
these signals and drives the actual work, then calls back into this
window's public ``display_*`` / ``show_*`` methods to update the UI.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from models.history_entry import HistoryEntry, MethodResultSnapshot
from utils.constants import ALL_METHODS, APP_NAME
from views.dialogs.about_dialog import AboutDialog
from views.dialogs.error_dialog import show_error, show_warning
from views.dialogs.history_dialog import HistoryDialog
from views.dialogs.settings_dialog import SettingsDialog
from views.widgets.comparison_widget import ComparisonWidget
from views.widgets.function_input_widget import FunctionInputWidget
from views.widgets.method_selector_widget import MethodSelectorWidget
from views.widgets.plot_widget import PlotWidget
from views.widgets.results_table_widget import ResultsTableWidget


class MainWindow(QMainWindow):
    """The application's primary window.

    Signals:
        compute_requested: (function_str, lower, upper, num_intervals, methods)
            Emitted when the user clicks "Compute" with valid-looking input.
        new_requested: Emitted from File > New.
        history_requested: Emitted from File > Open History (controller
            should respond by calling ``display_history_dialog``).
        export_pdf_requested: Emitted from File > Export PDF.
        export_csv_requested: Emitted from File > Export CSV.
        theme_change_requested: (theme_name) Emitted from View > Light/Dark.
        settings_saved: (settings_dict) Emitted after the Settings dialog
            is saved.
        compare_algorithms_requested: Emitted from Analysis > Compare Algorithms.
        convergence_analysis_requested: Emitted from Analysis > Convergence Analysis.
        history_entry_selected: (entry_id) Emitted when a history entry is
            reopened from the History dialog.
        history_entry_delete_requested: (entry_id) Emitted when a history
            entry's delete is requested from the History dialog.
    """

    compute_requested = Signal(str, float, float, int, list)
    new_requested = Signal()
    history_requested = Signal()
    export_pdf_requested = Signal()
    export_csv_requested = Signal()
    theme_change_requested = Signal(str)
    settings_saved = Signal(dict)
    compare_algorithms_requested = Signal()
    convergence_analysis_requested = Signal()
    history_entry_selected = Signal(int)
    history_entry_delete_requested = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 780)

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central_widget()
        self._build_status_bar()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        self.action_new = QAction("&New", self)
        self.action_new.setShortcut("Ctrl+N")
        self.action_new.triggered.connect(self.new_requested.emit)
        file_menu.addAction(self.action_new)

        self.action_open_history = QAction("&Open History", self)
        self.action_open_history.setShortcut("Ctrl+H")
        self.action_open_history.triggered.connect(self.history_requested.emit)
        file_menu.addAction(self.action_open_history)

        file_menu.addSeparator()

        self.action_export_pdf = QAction("Export &PDF", self)
        self.action_export_pdf.triggered.connect(self.export_pdf_requested.emit)
        file_menu.addAction(self.action_export_pdf)

        self.action_export_csv = QAction("Export &CSV", self)
        self.action_export_csv.triggered.connect(self.export_csv_requested.emit)
        file_menu.addAction(self.action_export_csv)

        file_menu.addSeparator()

        self.action_settings = QAction("&Settings", self)
        self.action_settings.triggered.connect(self._show_settings_dialog)
        file_menu.addAction(self.action_settings)

        file_menu.addSeparator()

        self.action_exit = QAction("E&xit", self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.triggered.connect(self.close)
        file_menu.addAction(self.action_exit)

        view_menu = menu_bar.addMenu("&View")
        self.action_light_theme = QAction("&Light Theme", self)
        self.action_light_theme.triggered.connect(lambda: self.theme_change_requested.emit("light"))
        view_menu.addAction(self.action_light_theme)

        self.action_dark_theme = QAction("&Dark Theme", self)
        self.action_dark_theme.triggered.connect(lambda: self.theme_change_requested.emit("dark"))
        view_menu.addAction(self.action_dark_theme)

        analysis_menu = menu_bar.addMenu("&Analysis")
        self.action_compare = QAction("&Compare Algorithms", self)
        self.action_compare.triggered.connect(self.compare_algorithms_requested.emit)
        analysis_menu.addAction(self.action_compare)

        self.action_convergence = QAction("Con&vergence Analysis", self)
        self.action_convergence.triggered.connect(self.convergence_analysis_requested.emit)
        analysis_menu.addAction(self.action_convergence)

        help_menu = menu_bar.addMenu("&Help")
        self.action_documentation = QAction("&Documentation", self)
        self.action_documentation.triggered.connect(self._show_documentation)
        help_menu.addAction(self.action_documentation)

        self.action_about = QAction("&About", self)
        self.action_about.triggered.connect(self._show_about_dialog)
        help_menu.addAction(self.action_about)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open_history)
        toolbar.addSeparator()
        toolbar.addAction(self.action_export_pdf)
        toolbar.addAction(self.action_export_csv)

    def _build_central_widget(self) -> None:
        splitter = QSplitter()

        # --- Sidebar: function input + method selection + compute button ---
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)

        function_group = QGroupBox("Function && Limits")
        function_group_layout = QVBoxLayout(function_group)
        self.function_input_widget = FunctionInputWidget()
        function_group_layout.addWidget(self.function_input_widget)
        sidebar_layout.addWidget(function_group)

        methods_group = QGroupBox("Methods")
        methods_group_layout = QVBoxLayout(methods_group)
        self.method_selector_widget = MethodSelectorWidget()
        methods_group_layout.addWidget(self.method_selector_widget)
        sidebar_layout.addWidget(methods_group)

        self.compute_button = QPushButton("Compute")
        self.compute_button.clicked.connect(self._on_compute_clicked)
        sidebar_layout.addWidget(self.compute_button)

        self.compute_all_button = QPushButton("Compute All Methods")
        self.compute_all_button.clicked.connect(self._on_compute_all_clicked)
        sidebar_layout.addWidget(self.compute_all_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setVisible(False)
        sidebar_layout.addWidget(self.progress_bar)

        sidebar_layout.addStretch()
        sidebar.setMaximumWidth(400)
        splitter.addWidget(sidebar)

        # --- Main area: tabbed results ---
        self.tab_widget = QTabWidget()

        self.results_table_widget = ResultsTableWidget()
        self.tab_widget.addTab(self.results_table_widget, "Results")

        self.plot_widget = PlotWidget()
        self.tab_widget.addTab(self.plot_widget, "Plot")

        self.comparison_widget = ComparisonWidget()
        self.tab_widget.addTab(self.comparison_widget, "Comparison")

        self.convergence_plot_widget = PlotWidget()
        self.tab_widget.addTab(self.convergence_plot_widget, "Convergence")

        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        self.setStatusBar(status_bar)

    # ------------------------------------------------------------------ #
    # Internal handlers
    # ------------------------------------------------------------------ #
    def _on_compute_clicked(self) -> None:
        """Gather sidebar input and emit ``compute_requested`` if valid enough
        to attempt (full mathematical validation happens downstream)."""
        self._emit_compute_request(self.method_selector_widget.selected_methods())

    def _on_compute_all_clicked(self) -> None:
        """Gather sidebar input and compute results for all supported methods."""
        self.method_selector_widget.set_selected_methods(list(ALL_METHODS))
        self._emit_compute_request(list(ALL_METHODS))

    def _emit_compute_request(self, methods: list[str]) -> None:
        self.function_input_widget.clear_error()

        function_text = self.function_input_widget.get_function_text()
        if not function_text:
            self.function_input_widget.set_error("Please enter a function, e.g. sin(x)")
            return

        if not methods:
            show_warning(self, "No Method Selected", "Please select at least one integration method.")
            return

        lower = self.function_input_widget.get_lower_limit()
        upper = self.function_input_widget.get_upper_limit()
        if lower >= upper:
            self.function_input_widget.set_error("Lower limit must be less than upper limit.")
            return

        intervals = self.function_input_widget.get_num_intervals()

        self.compute_requested.emit(function_text, lower, upper, intervals, methods)

    def _show_about_dialog(self) -> None:
        AboutDialog(self).exec()

    def _show_settings_dialog(self, current_settings: dict | None = None) -> None:
        dialog = SettingsDialog(current_settings or {}, self)
        dialog.settings_saved.connect(self.settings_saved.emit)
        dialog.exec()

    def _show_documentation(self) -> None:
        QMessageBox.information(
            self,
            "Documentation",
            "See docs/user_guide.md in the application folder for the full "
            "user guide, or docs/architecture.md for technical documentation.",
        )

    # ------------------------------------------------------------------ #
    # Public API for controllers to update this view
    # ------------------------------------------------------------------ #
    def display_results(self, results: list[MethodResultSnapshot]) -> None:
        """Populate the Results tab with fresh computation results."""
        self.results_table_widget.set_results(results)

    def display_comparison(self, results: list[MethodResultSnapshot]) -> None:
        """Populate the Comparison tab, highlighting the best method."""
        self.comparison_widget.set_comparison(results)

    def display_history_dialog(self, entries: list[HistoryEntry]) -> None:
        """Open the history dialog populated with the given entries."""
        dialog = HistoryDialog(entries, self)
        dialog.entry_selected.connect(self.history_entry_selected.emit)
        dialog.entry_delete_requested.connect(self.history_entry_delete_requested.emit)
        dialog.exec()

    def display_error(self, title: str, message: str) -> None:
        """Show a friendly modal error dialog."""
        show_error(self, title, message)

    def set_status_message(self, message: str) -> None:
        """Update the status bar's text."""
        self.status_label.setText(message)

    def show_busy(self, busy: bool) -> None:
        """Show or hide the indeterminate progress bar and disable/enable Compute."""
        self.progress_bar.setVisible(busy)
        self.compute_button.setEnabled(not busy)
