"""
Dialog for browsing and reopening previously saved calculations.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.history_entry import HistoryEntry

_COLUMNS = ("Date", "Function", "Limits", "Intervals", "Methods")


class HistoryDialog(QDialog):
    """Lists all stored history entries and lets the user reopen or delete one.

    Signals:
        entry_selected: Emitted with the ``id`` of the entry the user
            double-clicked (or selected and clicked "Open").
        entry_delete_requested: Emitted with the ``id`` of the entry the
            user asked to delete.
    """

    entry_selected = Signal(int)
    entry_delete_requested = Signal(int)

    def __init__(self, entries: list[HistoryEntry], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Calculation History")
        self.setMinimumSize(640, 400)
        self._entries = entries
        self._build_ui()
        self._populate(entries)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self._on_open_clicked)
        layout.addWidget(self.table)

        button_row = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self._on_open_clicked)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("secondaryButton")
        self.delete_button.clicked.connect(self._on_delete_clicked)
        button_row.addWidget(self.open_button)
        button_row.addWidget(self.delete_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, entries: list[HistoryEntry]) -> None:
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            values = (
                entry.timestamp.strftime("%Y-%m-%d %H:%M"),
                entry.function_expression,
                f"[{entry.lower_limit}, {entry.upper_limit}]",
                str(entry.num_intervals),
                ", ".join(entry.methods),
            )
            for col, text in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(text))

    def _selected_entry_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._entries):
            return None
        return self._entries[row].id

    def _on_open_clicked(self) -> None:
        entry_id = self._selected_entry_id()
        if entry_id is not None:
            self.entry_selected.emit(entry_id)
            self.accept()

    def _on_delete_clicked(self) -> None:
        entry_id = self._selected_entry_id()
        if entry_id is not None:
            self.entry_delete_requested.emit(entry_id)

    def refresh(self, entries: list[HistoryEntry]) -> None:
        """Reload the table with a new list of entries (e.g. after a delete).

        Args:
            entries: The updated list of history entries to display.
        """
        self._entries = entries
        self._populate(entries)
