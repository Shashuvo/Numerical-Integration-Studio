"""
Widget for entering the integrand, integration limits, and interval count.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from utils.constants import MAX_INTERVALS, MIN_INTERVALS, PREDEFINED_EQUATIONS


class FunctionInputWidget(QWidget):
    """Collects f(x), the lower/upper limits, and the number of intervals.

    This widget performs no validation of its own beyond basic numeric
    range constraints on the spin boxes (SymPy parsing and mathematical
    validation happen in the service layer). It exposes a simple
    getter/setter API and a signal so a controller can react to changes.

    Signals:
        input_changed: Emitted whenever any field's value changes.
    """

    input_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom")
        for name in PREDEFINED_EQUATIONS:
            self.preset_combo.addItem(name)
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        self.preset_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form.addRow(QLabel("Preset equation:"), self.preset_combo)

        self.function_edit = QLineEdit()
        self.function_edit.setPlaceholderText("e.g. sin(x)*exp(-x), x**2, sqrt(x)")
        self.function_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form.addRow(QLabel("f(x) ="), self.function_edit)

        self.lower_limit_spin = QDoubleSpinBox()
        self.lower_limit_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.lower_limit_spin.setDecimals(6)
        self.lower_limit_spin.setValue(0.0)
        self.lower_limit_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form.addRow(QLabel("Lower limit (a):"), self.lower_limit_spin)

        self.upper_limit_spin = QDoubleSpinBox()
        self.upper_limit_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.upper_limit_spin.setDecimals(6)
        self.upper_limit_spin.setValue(1.0)
        self.upper_limit_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form.addRow(QLabel("Upper limit (b):"), self.upper_limit_spin)

        self.intervals_spin = QSpinBox()
        self.intervals_spin.setRange(MIN_INTERVALS, MAX_INTERVALS)
        self.intervals_spin.setValue(100)
        self.intervals_spin.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        form.addRow(QLabel("Number of intervals (n):"), self.intervals_spin)

        layout.addLayout(form)

        self.validation_label = QLabel("")
        self.validation_label.setObjectName("errorLabel")
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)

    def _connect_signals(self) -> None:
        self.function_edit.textChanged.connect(lambda _text: self.input_changed.emit())
        self.lower_limit_spin.valueChanged.connect(lambda _value: self.input_changed.emit())
        self.upper_limit_spin.valueChanged.connect(lambda _value: self.input_changed.emit())
        self.intervals_spin.valueChanged.connect(lambda _value: self.input_changed.emit())
        self.preset_combo.currentTextChanged.connect(lambda _text: self.input_changed.emit())

    def get_function_text(self) -> str:
        """Return the raw function expression string as typed by the user."""
        return self.function_edit.text().strip()

    def _on_preset_selected(self, preset_name: str) -> None:
        preset = PREDEFINED_EQUATIONS.get(preset_name)
        if preset is None:
            return

        self.function_edit.setText(preset["expression"])
        self.lower_limit_spin.setValue(preset["lower"])
        self.upper_limit_spin.setValue(preset["upper"])
        self.intervals_spin.setValue(preset["intervals"])
        self.input_changed.emit()

    def get_lower_limit(self) -> float:
        """Return the current lower integration limit."""
        return self.lower_limit_spin.value()

    def get_upper_limit(self) -> float:
        """Return the current upper integration limit."""
        return self.upper_limit_spin.value()

    def get_num_intervals(self) -> int:
        """Return the current number of intervals."""
        return self.intervals_spin.value()

    def set_error(self, message: str) -> None:
        """Display a validation error message and highlight the function field.

        Args:
            message: Friendly error text to show under the form. Pass an
                empty string to clear the error state.
        """
        self.validation_label.setText(message)
        self.function_edit.setObjectName("invalidInput" if message else "")
        self.function_edit.style().unpolish(self.function_edit)
        self.function_edit.style().polish(self.function_edit)

    def clear_error(self) -> None:
        """Clear any displayed validation error."""
        self.set_error("")
