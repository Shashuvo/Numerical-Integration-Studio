"""
Widget for side-by-side comparison of all computed methods, with the
most accurate method highlighted.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
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

_BEST_ROW_COLOR = QColor("#D9F2E1")  # soft green highlight, theme-independent
_BEST_ROW_TEXT_COLOR = QColor("#1E2130")  # dark text for highlighted rows


class ComparisonWidget(QTableWidget):
    """Displays a comparison table and highlights the most accurate method.

    "Most accurate" is defined as the method with the smallest absolute
    error among results that have a known exact value. If no result has
    a known absolute error (no exact value could be computed), no row
    is highlighted.
    """

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

    def set_comparison(self, results: list[MethodResultSnapshot]) -> None:
        """Populate the comparison table and highlight the best-performing row.

        Args:
            results: One snapshot per method being compared.
        """
        self.setRowCount(len(results))

        best_index = self._find_best_index(results)

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
                if row == best_index:
                    item.setBackground(_BEST_ROW_COLOR)
                    item.setForeground(_BEST_ROW_TEXT_COLOR)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.setItem(row, col, item)

    @staticmethod
    def _find_best_index(results: list[MethodResultSnapshot]) -> int | None:
        """Return the index of the result with the smallest absolute error.

        Args:
            results: The results to compare.

        Returns:
            The index of the best result, or ``None`` if no result has
            a usable absolute error value.
        """
        best_index: int | None = None
        best_error = float("inf")
        for i, result in enumerate(results):
            if result.absolute_error is not None and result.absolute_error < best_error:
                best_error = result.absolute_error
                best_index = i
        return best_index

    def clear_comparison(self) -> None:
        """Remove all rows from the table."""
        self.setRowCount(0)
