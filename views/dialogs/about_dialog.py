"""
"About" dialog showing application name, version, and description.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from utils.constants import APP_NAME, APP_VERSION


class AboutDialog(QDialog):
    """A simple modal dialog describing the application."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title_label = QLabel(APP_NAME)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        description = QLabel(
            "An educational desktop application for approximating definite "
            "integrals using the Trapezoidal Rule, Simpson's 1/3 Rule, "
            "Simpson's 3/8 Rule, and Taylor's Method — with visualization, "
            "error analysis, convergence analysis, and report generation.\n\n"
            "Built with Python, PySide6, NumPy, SciPy, SymPy, Matplotlib, "
            "and ReportLab.\n\n"
            "Build by MD. Shahariat Hossen.\n" 
            "Github link: https://github.com/Shashuvo"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
