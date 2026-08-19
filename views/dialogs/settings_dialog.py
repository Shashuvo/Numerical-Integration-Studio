"""
Application settings dialog (theme, default precision, default intervals).

This dialog only handles presentation and emits the chosen values via
a signal; persisting them to ``config.yaml`` is the responsibility of
``utils.config_manager`` (wired up by a controller), keeping this view
decoupled from how/where settings are stored.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    """Lets the user adjust application-wide preferences.

    Signals:
        settings_saved: Emitted with a dict of the chosen settings when
            the user clicks OK/Save.
    """

    settings_saved = Signal(dict)

    def __init__(self, current_settings: dict[str, Any] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(340)
        self._current_settings = current_settings or {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = self._current_settings.get("theme", "light")
        self.theme_combo.setCurrentText(current_theme.capitalize())
        form.addRow("Theme:", self.theme_combo)

        self.precision_spin = QSpinBox()
        self.precision_spin.setRange(2, 15)
        self.precision_spin.setValue(self._current_settings.get("decimal_precision", 8))
        form.addRow("Decimal precision:", self.precision_spin)

        self.default_intervals_spin = QSpinBox()
        self.default_intervals_spin.setRange(1, 1_000_000)
        self.default_intervals_spin.setValue(self._current_settings.get("default_intervals", 100))
        form.addRow("Default intervals:", self.default_intervals_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save(self) -> None:
        """Collect current field values, emit them, and close the dialog."""
        settings = {
            "theme": self.theme_combo.currentText().lower(),
            "decimal_precision": self.precision_spin.value(),
            "default_intervals": self.default_intervals_spin.value(),
        }
        self.settings_saved.emit(settings)
        self.accept()
