"""
Taylor's Method for numerical integration.

NOTE ON SCOPE: "Taylor's Method" is not a single universally standardized
integration rule the way the Trapezoidal/Simpson rules are — different
courses define it at different orders. This implementation uses the
widely-taught 4th-order Taylor series method, applied to the equivalent
initial value problem y' = f(x), y(a) = 0, whose solution at x = b is
the definite integral. If your course specifies a different order or
formulation, adjust the ``TAYLOR_ORDER`` constant below (and the
step formula in ``_compute`` accordingly) — this file is the single
place that would need to change.
"""

from __future__ import annotations

import math

from algorithms.base_algorithm import BaseAlgorithm
from models.function_model import FunctionModel
from utils.constants import METHOD_TAYLOR

#: Number of Taylor series terms used per step (order 4 = terms through h^4).
TAYLOR_ORDER = 4


class TaylorMethod(BaseAlgorithm):
    """Approximates the integral via a 4th-order Taylor series step method.

    Treats the integral as the solution to the initial value problem
    y'(x) = f(x), y(a) = 0, so y^(k)(x) = f^(k-1)(x). Steps forward from
    x = a to x = b using:

        y_{i+1} = y_i + sum_{k=1}^{4} (h^k / k!) * f^(k-1)(x_i)

    where h = (b - a) / n is the step size. y_n is the approximation
    of the definite integral.
    """

    method_key = METHOD_TAYLOR

    def _compute(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> tuple[float, int]:
        h = (upper - lower) / num_intervals

        # f^(0) = f itself; f^(1), f^(2), f^(3) are its symbolic derivatives.
        # Precomputed once and reused at every step for efficiency.
        derivatives = [function_model] + [
            function_model.derivative(order) for order in range(1, TAYLOR_ORDER)
        ]

        y = 0.0
        x_i = lower
        for _ in range(num_intervals):
            increment = 0.0
            for k in range(1, TAYLOR_ORDER + 1):
                # y^(k) at x_i equals f^(k-1) at x_i
                f_derivative_value = derivatives[k - 1].evaluate(x_i)
                increment += (h ** k / math.factorial(k)) * f_derivative_value
            y += increment
            x_i += h

        return y, num_intervals
