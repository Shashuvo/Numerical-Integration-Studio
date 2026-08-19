"""
Draws the integrand, the shaded integration area, and each selected
method's sampled approximation nodes onto a ``PlotWidget``.
"""

from __future__ import annotations

import numpy as np

from models.function_model import FunctionModel
from models.integration_result import IntegrationResult
from utils.constants import METHOD_DISPLAY_NAMES
from utils.exceptions import IntegrationDomainError
from utils.logger import get_logger
from views.widgets.plot_widget import PlotWidget

_logger = get_logger(__name__)

# Distinct colors per method so overlays stay visually separable.
_METHOD_COLORS = {
    "trapezoidal": "#E07A5F",
    "simpson_1_3": "#3D9970",
    "simpson_3_8": "#8C6FD9",
    "taylor": "#D9A441",
}

_CURVE_SAMPLE_COUNT = 400
_CURVE_MARGIN_FRACTION = 0.1


class FunctionPlotter:
    """Renders the function curve, shaded integration area, and per-method
    sample nodes onto a shared ``PlotWidget`` figure."""

    def plot(
        self,
        plot_widget: PlotWidget,
        function_model: FunctionModel,
        lower: float,
        upper: float,
        integration_results: list[IntegrationResult],
    ) -> None:
        """Draw the full function/approximation visualization.

        Args:
            plot_widget: The widget to draw onto (its figure is cleared first).
            function_model: The function being integrated.
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            integration_results: One result per method the user selected,
                used to overlay each method's sample nodes.
        """
        plot_widget.figure.clear()
        axes = plot_widget.figure.add_subplot(111)

        span = upper - lower
        margin = span * _CURVE_MARGIN_FRACTION if span > 0 else 1.0
        curve_x = np.linspace(lower - margin, upper + margin, _CURVE_SAMPLE_COUNT)
        curve_y = self._safe_evaluate_array(function_model, curve_x)

        axes.plot(curve_x, curve_y, color="#4C5B8C", linewidth=2, label=f"f(x) = {function_model.source_text}")

        # Shade the area actually being integrated, using a finer sample
        # restricted to [lower, upper] so the fill follows the curve closely.
        fill_x = np.linspace(lower, upper, _CURVE_SAMPLE_COUNT)
        fill_y = self._safe_evaluate_array(function_model, fill_x)
        axes.fill_between(fill_x, fill_y, 0, color="#4C5B8C", alpha=0.15, label="Integration area")

        for result in integration_results:
            self._overlay_method_nodes(axes, function_model, result)

        axes.axvline(lower, color="#8A8FA5", linestyle="--", linewidth=1)
        axes.axvline(upper, color="#8A8FA5", linestyle="--", linewidth=1)

        axes.set_xlabel("x")
        axes.set_ylabel("f(x)")
        axes.set_title("Function and Approximation Nodes")
        axes.legend(loc="best", fontsize=8)
        axes.grid(True, alpha=0.3)

        plot_widget.redraw()

    def _overlay_method_nodes(self, axes, function_model: FunctionModel, result: IntegrationResult) -> None:
        """Plot the sample nodes a method evaluated, connected by a thin line."""
        node_x = np.linspace(result.lower_limit, result.upper_limit, result.num_intervals + 1)
        node_y = self._safe_evaluate_array(function_model, node_x)

        color = _METHOD_COLORS.get(result.method_name, "#333333")
        display_name = METHOD_DISPLAY_NAMES.get(result.method_name, result.method_name)

        axes.plot(
            node_x, node_y,
            marker="o", markersize=3, linewidth=1, linestyle="-",
            color=color, alpha=0.75, label=f"{display_name} nodes",
        )

    @staticmethod
    def _safe_evaluate_array(function_model: FunctionModel, x_values: np.ndarray) -> np.ndarray:
        """Evaluate f(x) over an array, substituting NaN where undefined
        so plotting can continue (Matplotlib skips NaN points automatically)."""
        y_values = np.empty_like(x_values, dtype=float)
        for i, x in enumerate(x_values):
            try:
                y_values[i] = function_model.evaluate(float(x))
            except IntegrationDomainError:
                y_values[i] = np.nan
        return y_values
