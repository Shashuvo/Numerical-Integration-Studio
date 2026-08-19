"""
Draws Error-vs-N and Execution-Time-vs-N convergence plots onto a
``PlotWidget``, one line per method being compared.
"""

from __future__ import annotations

from services.convergence_service import ConvergenceDataPoint
from utils.constants import METHOD_DISPLAY_NAMES
from views.widgets.plot_widget import PlotWidget

_METHOD_COLORS = {
    "trapezoidal": "#E07A5F",
    "simpson_1_3": "#3D9970",
    "simpson_3_8": "#8C6FD9",
    "taylor": "#D9A441",
}


class ConvergencePlotter:
    """Renders paired convergence plots (error vs n, time vs n) for one
    or more methods onto a single shared ``PlotWidget`` figure."""

    def plot(
        self,
        plot_widget: PlotWidget,
        data_points_by_method: dict[str, list[ConvergenceDataPoint]],
    ) -> None:
        """Draw the two-panel convergence visualization.

        Args:
            plot_widget: The widget to draw onto (its figure is cleared first).
            data_points_by_method: Maps method key to its list of
                ``ConvergenceDataPoint`` samples (as produced by
                ``ConvergenceService.run_sweep``).
        """
        plot_widget.figure.clear()
        error_axes = plot_widget.figure.add_subplot(211)
        time_axes = plot_widget.figure.add_subplot(212)

        any_error_data = False

        for method_key, points in data_points_by_method.items():
            if not points:
                continue

            color = _METHOD_COLORS.get(method_key, "#333333")
            display_name = METHOD_DISPLAY_NAMES.get(method_key, method_key)

            ns = [p.num_intervals for p in points]
            times = [p.execution_time_seconds for p in points]
            time_axes.plot(ns, times, marker="s", markersize=4, color=color, label=display_name)

            errors = [p.absolute_error for p in points if p.absolute_error is not None]
            error_ns = [p.num_intervals for p in points if p.absolute_error is not None]
            if errors:
                any_error_data = True
                # Errors span many orders of magnitude across methods/n,
                # so a log scale is essential for a readable comparison.
                error_axes.semilogy(error_ns, errors, marker="o", markersize=4, color=color, label=display_name)

        error_axes.set_xlabel("Number of Intervals (n)")
        error_axes.set_ylabel("Absolute Error (log scale)")
        error_axes.set_title("Convergence: Error vs. Number of Intervals")
        error_axes.grid(True, which="both", alpha=0.3)
        if any_error_data:
            error_axes.legend(loc="best", fontsize=8)
        else:
            error_axes.text(
                0.5, 0.5, "No exact value available — error data not shown",
                ha="center", va="center", transform=error_axes.transAxes, fontsize=9, color="#8A8FA5",
            )

        time_axes.set_xlabel("Number of Intervals (n)")
        time_axes.set_ylabel("Execution Time (s)")
        time_axes.set_title("Convergence: Execution Time vs. Number of Intervals")
        time_axes.grid(True, alpha=0.3)
        time_axes.legend(loc="best", fontsize=8)

        plot_widget.figure.tight_layout()
        plot_widget.redraw()
