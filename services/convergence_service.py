"""
Runs a single algorithm across a range of interval counts to measure
how error and execution time change as n grows (convergence behavior).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from algorithms.algorithm_factory import AlgorithmFactory
from models.function_model import FunctionModel
from utils.constants import METHOD_SIMPSON_1_3, METHOD_SIMPSON_3_8
from utils.logger import get_logger

_logger = get_logger(__name__)


@dataclass
class ConvergenceDataPoint:
    """One (n, error, time) sample from a convergence sweep.

    Attributes:
        num_intervals: The number of intervals used for this run.
        absolute_error: |approx - exact|, or None if no exact value
            could be determined for the function.
        execution_time_seconds: Wall-clock time this run took.
    """

    num_intervals: int
    absolute_error: Optional[float]
    execution_time_seconds: float


class ConvergenceService:
    """Sweeps a range of n values for a single method and records
    error/time behavior, for use in convergence plots."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def valid_intervals_for_method(self, method_key: str, requested_intervals: list[int]) -> list[int]:
        """Filter a list of candidate n values down to ones valid for a method.

        Args:
            method_key: The canonical method key.
            requested_intervals: Candidate interval counts to consider.

        Returns:
            The subset of ``requested_intervals`` that satisfy the
            method's constraints (e.g. even for Simpson 1/3, multiple
            of 3 for Simpson 3/8), preserving order and deduplicating.
        """
        if method_key == METHOD_SIMPSON_1_3:
            valid = [n for n in requested_intervals if n % 2 == 0]
        elif method_key == METHOD_SIMPSON_3_8:
            valid = [n for n in requested_intervals if n % 3 == 0]
        else:
            valid = list(requested_intervals)
        return sorted(set(n for n in valid if n > 0))

    def run_sweep(
        self,
        function_model: FunctionModel,
        method_key: str,
        lower: float,
        upper: float,
        requested_intervals: list[int],
    ) -> list[ConvergenceDataPoint]:
        """Run one method across a range of interval counts.

        Args:
            function_model: The function being integrated.
            method_key: The canonical method key to sweep.
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            requested_intervals: Candidate n values to try (invalid ones
                for this method, e.g. odd n for Simpson 1/3, are skipped).

        Returns:
            One ``ConvergenceDataPoint`` per successfully-run n value,
            sorted by n ascending.
        """
        exact_value = function_model.exact_definite_integral(lower, upper)
        valid_intervals = self.valid_intervals_for_method(method_key, requested_intervals)

        data_points: list[ConvergenceDataPoint] = []
        for n in valid_intervals:
            algorithm = AlgorithmFactory.create(method_key)
            try:
                result = algorithm.integrate(function_model, lower, upper, n)
            except Exception as exc:  # noqa: BLE001 - skip and log any run failure
                self._logger.warning(
                    "Convergence sweep: skipping n=%s for %s due to error: %s",
                    n, method_key, exc,
                )
                continue

            absolute_error = (
                abs(result.approximate_value - exact_value) if exact_value is not None else None
            )
            data_points.append(
                ConvergenceDataPoint(
                    num_intervals=n,
                    absolute_error=absolute_error,
                    execution_time_seconds=result.execution_time_seconds,
                )
            )

        return data_points
