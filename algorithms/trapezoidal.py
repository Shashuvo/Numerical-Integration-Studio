"""
Trapezoidal Rule for numerical integration.
"""

from __future__ import annotations

from algorithms.base_algorithm import BaseAlgorithm
from models.function_model import FunctionModel
from utils.constants import METHOD_TRAPEZOIDAL


class TrapezoidalRule(BaseAlgorithm):
    """Approximates the integral by summing trapezoids under the curve.

    Formula (n intervals of width h = (b - a) / n):

        integral ≈ h/2 * [f(x0) + 2*f(x1) + 2*f(x2) + ... + 2*f(x_{n-1}) + f(xn)]
    """

    method_key = METHOD_TRAPEZOIDAL

    def _compute(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> tuple[float, int]:
        h = (upper - lower) / num_intervals
        total = function_model.evaluate(lower) + function_model.evaluate(upper)

        for i in range(1, num_intervals):
            x_i = lower + i * h
            total += 2.0 * function_model.evaluate(x_i)

        return (h / 2.0) * total, num_intervals
