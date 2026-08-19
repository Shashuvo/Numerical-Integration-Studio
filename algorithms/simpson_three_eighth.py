"""
Simpson's 3/8 Rule for numerical integration.
"""

from __future__ import annotations

from algorithms.base_algorithm import BaseAlgorithm
from models.function_model import FunctionModel
from utils.constants import METHOD_SIMPSON_3_8
from utils.logger import get_logger

_logger = get_logger(__name__)


class SimpsonThreeEighthRule(BaseAlgorithm):
    """Approximates the integral using cubic arcs over groups of 3 intervals.

    Requires the number of intervals to be a multiple of 3. If not, it
    is automatically rounded up to the next multiple of 3 (rather than
    rejecting the request) — the actual value used is reported back via
    the returned ``IntegrationResult.num_intervals``, so callers running
    several methods side by side don't have their whole computation
    fail over one method's constraint.

    Formula (n intervals, h = (b-a)/n):

        integral ≈ 3h/8 * [f(x0) + 3*(non-multiple-of-3 indices)
                            + 2*(multiples of 3, interior) + f(xn)]
    """

    method_key = METHOD_SIMPSON_3_8

    def _compute(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> tuple[float, int]:
        if num_intervals % 3 != 0:
            adjusted = num_intervals + (3 - num_intervals % 3)
            _logger.info(
                "Simpson's 3/8 Rule: n=%d is not a multiple of 3; rounding up to n=%d",
                num_intervals, adjusted,
            )
            num_intervals = adjusted

        h = (upper - lower) / num_intervals
        total = function_model.evaluate(lower) + function_model.evaluate(upper)

        for i in range(1, num_intervals):
            x_i = lower + i * h
            weight = 2.0 if i % 3 == 0 else 3.0
            total += weight * function_model.evaluate(x_i)

        return (3.0 * h / 8.0) * total, num_intervals
