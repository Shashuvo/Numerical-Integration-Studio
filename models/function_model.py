"""
Wraps a parsed SymPy expression in x, providing safe numeric evaluation,
symbolic differentiation, and (where possible) an exact definite integral.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Optional

import sympy
from sympy import Symbol

from utils.exceptions import IntegrationDomainError
from utils.logger import get_logger

_logger = get_logger(__name__)


class FunctionModel:
    """A validated, evaluable mathematical function of a single variable x.

    Instances are typically created by ``services.expression_parser
    .ExpressionParserService.parse``, not constructed directly, so the
    expression is guaranteed to be in terms of ``x`` only.

    Attributes:
        expression: The parsed SymPy expression.
        symbol: The SymPy symbol used for the independent variable (x).
        source_text: The original, user-entered expression string.
    """

    def __init__(self, expression: sympy.Expr, symbol: Symbol, source_text: str) -> None:
        self.expression = expression
        self.symbol = symbol
        self.source_text = source_text
        self._numeric_func: Optional[Callable[[float], complex]] = None

    def _lambdified(self) -> Callable[[float], complex]:
        """Lazily build and cache the numeric (NumPy-backed) callable."""
        if self._numeric_func is None:
            self._numeric_func = sympy.lambdify(
                self.symbol, self.expression, modules=["numpy"]
            )
        return self._numeric_func

    def evaluate(self, x_value: float) -> float:
        """Evaluate f(x_value) as a real float.

        Args:
            x_value: The point at which to evaluate the function.

        Returns:
            The real-valued result of f(x_value).

        Raises:
            IntegrationDomainError: If the function is undefined at
                ``x_value`` (division by zero, log of a non-positive
                number, resulting in a complex value, NaN, or infinity).
        """
        func = self._lambdified()
        try:
            result = func(x_value)
        except (ZeroDivisionError, ValueError, OverflowError, FloatingPointError) as exc:
            raise IntegrationDomainError(
                f"f(x) = {self.source_text} is undefined at x = {x_value}: {exc}"
            ) from exc

        result_complex = complex(result)
        if abs(result_complex.imag) > 1e-9:
            raise IntegrationDomainError(
                f"f(x) = {self.source_text} produced a complex value at x = {x_value}. "
                "The function may be undefined (e.g. sqrt of a negative number) "
                "somewhere on the given interval."
            )

        real_result = result_complex.real
        if real_result != real_result or real_result in (float("inf"), float("-inf")):
            raise IntegrationDomainError(
                f"f(x) = {self.source_text} is undefined (NaN/infinite) at x = {x_value}."
            )
        return real_result

    @lru_cache(maxsize=8)
    def _symbolic_derivative(self, order: int) -> sympy.Expr:
        """Compute (and cache) the symbolic nth derivative."""
        return sympy.diff(self.expression, self.symbol, order)

    def derivative(self, order: int) -> "FunctionModel":
        """Return a new ``FunctionModel`` for the nth derivative of this function.

        Args:
            order: The order of differentiation (1 = f', 2 = f'', ...).

        Returns:
            A ``FunctionModel`` wrapping d^order/dx^order of this expression.
        """
        derivative_expr = self._symbolic_derivative(order)
        return FunctionModel(
            expression=derivative_expr,
            symbol=self.symbol,
            source_text=f"d^{order}/dx^{order}[{self.source_text}]",
        )

    def exact_definite_integral(self, lower: float, upper: float) -> Optional[float]:
        """Attempt to compute the exact definite integral symbolically.

        Args:
            lower: Lower limit of integration.
            upper: Upper limit of integration.

        Returns:
            The exact value as a float if SymPy can find a closed form
            and evaluate it to a real number, otherwise ``None`` (no
            exact value could be determined).
        """
        try:
            integral = sympy.integrate(self.expression, (self.symbol, lower, upper))
            evaluated = integral.evalf()
        except Exception as exc:  # noqa: BLE001 - SymPy can raise many internal types
            _logger.debug("Symbolic integration failed for %s: %s", self.source_text, exc)
            return None

        if evaluated.is_number is False or evaluated.has(sympy.Symbol):
            return None
        if evaluated.is_real is False:
            return None

        try:
            return float(evaluated)
        except (TypeError, ValueError):
            return None
