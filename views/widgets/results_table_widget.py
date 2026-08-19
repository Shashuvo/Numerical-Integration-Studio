"""
Widget displaying computation results in tabular form.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget

from models.history_entry import MethodResultSnapshot
from utils.constants import METHOD_DISPLAY_NAMES

_COLUMNS = (
    "Method",
    "Approximation",
    "Exact Value",
    "Absolute Error",
    "Relative Error",
    "Execution Time (s)",
)


class ResultsTableWidget(QTableWidget):
    """Read-only table listing one row per computed method result."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(len(_COLUMNS))
        self.setHorizontalHeaderLabels(_COLUMNS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, len(_COLUMNS)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

    def set_results(self, results: list[MethodResultSnapshot]) -> None:
        """Populate the table with a fresh set of method results.

        Args:
            results: One snapshot per method that was computed.
        """
        self.setRowCount(len(results))
        for row, result in enumerate(results):
            display_name = METHOD_DISPLAY_NAMES.get(result.method_name, result.method_name)
            values = (
                display_name,
                f"{result.approximate_value:.8f}",
                f"{result.exact_value:.8f}" if result.exact_value is not None else "N/A",
                f"{result.absolute_error:.3e}" if result.absolute_error is not None else "N/A",
                f"{result.relative_error:.3e}" if result.relative_error is not None else "N/A",
                f"{result.execution_time_seconds:.6f}",
            )
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col, item)

    def clear_results(self) -> None:
        """Remove all rows from the table."""
        self.setRowCount(0)
