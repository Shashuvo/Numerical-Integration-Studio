"""
Controller that runs a convergence sweep and renders it onto a PlotWidget.
"""

from __future__ import annotations

from models.function_model import FunctionModel
from plots.convergence_plotter import ConvergencePlotter
from services.convergence_service import ConvergenceService
from utils.logger import get_logger
from views.widgets.plot_widget import PlotWidget


class ConvergenceController:
    """Sweeps a range of interval counts for each selected method and
    renders the resulting error/time-vs-n plots."""

    def __init__(
        self, convergence_service: ConvergenceService, convergence_plotter: ConvergencePlotter
    ) -> None:
        self._convergence_service = convergence_service
        self._convergence_plotter = convergence_plotter
        self._logger = get_logger(__name__)

    def run_and_plot(
        self,
        plot_widget: PlotWidget,
        function_model: FunctionModel,
        lower: float,
        upper: float,
        methods: list[str],
        base_num_intervals: int,
    ) -> None:
        """Run the sweep for each method and draw the convergence plots.

        Args:
            plot_widget: The widget to render the two-panel plot onto.
            function_model: The function being analyzed.
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            methods: Canonical method keys to include in the sweep.
            base_num_intervals: The user's currently entered interval
                count; the sweep uses fractions/multiples of this value
                as candidate n values.
        """
        multipliers = (0.125, 0.25, 0.5, 1, 2, 4, 8)
        candidate_intervals = sorted(
            {max(1, round(base_num_intervals * m)) for m in multipliers}
        )

        data_by_method = {}
        for method_key in methods:
            data_by_method[method_key] = self._convergence_service.run_sweep(
                function_model, method_key, lower, upper, candidate_intervals
            )

        self._convergence_plotter.plot(plot_widget, data_by_method)
        self._logger.info(
            "Ran convergence sweep for methods %s over n in %s", methods, candidate_intervals
        )
