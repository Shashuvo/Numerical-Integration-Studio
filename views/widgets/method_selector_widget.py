"""
Widget presenting checkboxes for the four supported integration methods.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from utils.constants import ALL_METHODS, METHOD_DISPLAY_NAMES, METHOD_TRAPEZOIDAL


class MethodSelectorWidget(QWidget):
    """Lets the user select one or more numerical integration methods.

    Signals:
        selection_changed: Emitted whenever any checkbox is toggled.
    """

    selection_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._checkboxes: dict[str, QCheckBox] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        for method_key in ALL_METHODS:
            checkbox = QCheckBox(METHOD_DISPLAY_NAMES[method_key])
            checkbox.setChecked(method_key == METHOD_TRAPEZOIDAL)
            checkbox.toggled.connect(self.selection_changed.emit)
            self._checkboxes[method_key] = checkbox
            layout.addWidget(checkbox)

    def selected_methods(self) -> list[str]:
        """Return the canonical keys of all currently checked methods.

        Returns:
            A list of method keys (e.g. ["trapezoidal", "simpson_1_3"]),
            in the fixed display order defined by ``ALL_METHODS``.
        """
        return [key for key, box in self._checkboxes.items() if box.isChecked()]

    def set_selected_methods(self, method_keys: list[str]) -> None:
        """Check exactly the given methods and uncheck all others.

        Args:
            method_keys: Canonical method keys to check.
        """
        for key, box in self._checkboxes.items():
            box.blockSignals(True)
            box.setChecked(key in method_keys)
            box.blockSignals(False)
        self.selection_changed.emit()

    def has_selection(self) -> bool:
        """Return True if at least one method is currently checked."""
        return len(self.selected_methods()) > 0
