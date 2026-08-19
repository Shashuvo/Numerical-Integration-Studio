"""
Simpson's 1/3 Rule for numerical integration.
"""

from __future__ import annotations

from algorithms.base_algorithm import BaseAlgorithm
from models.function_model import FunctionModel
from utils.constants import METHOD_SIMPSON_1_3
from utils.logger import get_logger

_logger = get_logger(__name__)


class SimpsonOneThirdRule(BaseAlgorithm):
    """Approximates the integral using parabolic arcs over pairs of intervals.

    Requires an even number of intervals. If an odd ``num_intervals`` is
    requested, it is automatically rounded up to the next even number
    (rather than rejecting the request) — the actual value used is
    reported back via the returned ``IntegrationResult.num_intervals``,
    so callers running several methods side by side (some requiring
    even n, some requiring multiples of 3) don't have their whole
    computation fail over one method's constraint.

    Formula (n intervals of width h = (b - a) / n):

        integral ≈ h/3 * [f(x0) + 4*(odd-indexed) + 2*(even-indexed, interior) + f(xn)]
    """

    method_key = METHOD_SIMPSON_1_3

    def _compute(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> tuple[float, int]:
        if num_intervals % 2 != 0:
            adjusted = num_intervals + 1
            _logger.info(
                "Simpson's 1/3 Rule: n=%d is odd; rounding up to n=%d", num_intervals, adjusted
            )
            num_intervals = adjusted

        h = (upper - lower) / num_intervals
        total = function_model.evaluate(lower) + function_model.evaluate(upper)

        for i in range(1, num_intervals):
            x_i = lower + i * h
            weight = 4.0 if i % 2 != 0 else 2.0
            total += weight * function_model.evaluate(x_i)

        return (h / 3.0) * total, num_intervals
