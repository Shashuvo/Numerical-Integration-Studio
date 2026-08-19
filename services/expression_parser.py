"""
Parses user-entered function strings (e.g. "sin(x)*exp(-x)") into
validated ``FunctionModel`` instances using SymPy.
"""

from __future__ import annotations

import tokenize

import sympy
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from models.function_model import FunctionModel
from utils.exceptions import ExpressionParsingError
from utils.logger import get_logger

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)
_ALLOWED_SYMBOL_NAME = "x"

# Caret is common in user-entered math ("x^2") but SymPy's parser treats
# ^ as XOR. Translating it to ** up front avoids a confusing parse error.
_CARET_REPLACEMENT = "**"


class ExpressionParserService:
    """Converts raw function strings into safe, evaluable ``FunctionModel``s."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)
        self._symbol = sympy.Symbol(_ALLOWED_SYMBOL_NAME)

    def parse(self, expression_text: str) -> FunctionModel:
        """Parse and validate a function string.

        Args:
            expression_text: The raw expression as typed by the user,
                e.g. "sin(x)", "x^2 + 1", "sqrt(x)".

        Returns:
            A ``FunctionModel`` wrapping the parsed expression.

        Raises:
            ExpressionParsingError: If the text is empty, cannot be
                parsed, or references any variable other than ``x``.
        """
        if not expression_text or not expression_text.strip():
            raise ExpressionParsingError("Please enter a function, e.g. sin(x).")

        normalized_text = expression_text.strip().replace("^", _CARET_REPLACEMENT)

        try:
            expression = parse_expr(
                normalized_text,
                local_dict={_ALLOWED_SYMBOL_NAME: self._symbol},
                transformations=_TRANSFORMATIONS,
            )
        except (SyntaxError, TypeError, ValueError, tokenize.TokenError) as exc:
            self._logger.info("Failed to parse expression '%s': %s", expression_text, exc)
            raise ExpressionParsingError(
                f"'{expression_text}' is not a valid mathematical expression. "
                "Try something like sin(x), x^2, exp(x), or sqrt(x)."
            ) from exc

        free_symbols = expression.free_symbols
        disallowed = free_symbols - {self._symbol}
        if disallowed:
            names = ", ".join(sorted(str(s) for s in disallowed))
            raise ExpressionParsingError(
                f"Only 'x' may be used as a variable. Found unsupported "
                f"symbol(s): {names}."
            )

        return FunctionModel(
            expression=expression, symbol=self._symbol, source_text=expression_text.strip()
        )
