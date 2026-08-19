"""
Computes absolute/relative/percentage error and builds the display-ready
``MethodResultSnapshot`` from a raw ``IntegrationResult``.
"""

from __future__ import annotations

from typing import Optional

from models.history_entry import MethodResultSnapshot
from models.integration_result import IntegrationResult


class ErrorAnalysisService:
    """Combines a raw algorithm result with a (possibly unknown) exact
    value to produce error metrics and the final display/storage model."""

    @staticmethod
    def compute_absolute_error(approximate_value: float, exact_value: Optional[float]) -> Optional[float]:
        """Return |approx - exact|, or None if no exact value is known."""
        if exact_value is None:
            return None
        return abs(approximate_value - exact_value)

    @staticmethod
    def compute_relative_error(approximate_value: float, exact_value: Optional[float]) -> Optional[float]:
        """Return |approx - exact| / |exact|, or None if exact is unknown or zero."""
        if exact_value is None or exact_value == 0:
            return None
        return abs(approximate_value - exact_value) / abs(exact_value)

    @staticmethod
    def compute_percentage_error(relative_error: Optional[float]) -> Optional[float]:
        """Convert a relative error fraction to a percentage, or None if unavailable."""
        if relative_error is None:
            return None
        return relative_error * 100.0

    def build_snapshot(
        self, result: IntegrationResult, exact_value: Optional[float]
    ) -> MethodResultSnapshot:
        """Build the full ``MethodResultSnapshot`` for one algorithm's result.

        Args:
            result: The raw output of ``BaseAlgorithm.integrate()``.
            exact_value: The SymPy-computed exact value, or None if no
                closed form could be found for this function.

        Returns:
            A ``MethodResultSnapshot`` with all error metrics populated
            (or left as None where an exact value isn't available).
        """
        absolute_error = self.compute_absolute_error(result.approximate_value, exact_value)
        relative_error = self.compute_relative_error(result.approximate_value, exact_value)
        percentage_error = self.compute_percentage_error(relative_error)

        return MethodResultSnapshot(
            method_name=result.method_name,
            approximate_value=result.approximate_value,
            exact_value=exact_value,
            absolute_error=absolute_error,
            relative_error=relative_error,
            percentage_error=percentage_error,
            execution_time_seconds=result.execution_time_seconds,
        )

    @staticmethod
    def find_best_method_index(results: list[MethodResultSnapshot]) -> Optional[int]:
        """Return the index of the result with the smallest absolute error.

        Args:
            results: The results to compare.

        Returns:
            The index of the most accurate result, or None if no result
            has a usable absolute error (e.g. no exact value was found).
        """
        best_index: Optional[int] = None
        best_error = float("inf")
        for i, result in enumerate(results):
            if result.absolute_error is not None and result.absolute_error < best_error:
                best_error = result.absolute_error
                best_index = i
        return best_index
