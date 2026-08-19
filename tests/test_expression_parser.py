"""
Tests for ExpressionParserService and FunctionModel.
"""

from __future__ import annotations

import pytest

from utils.exceptions import ExpressionParsingError, IntegrationDomainError


class TestValidParsing:
    @pytest.mark.parametrize(
        "expression,test_point,expected",
        [
            ("sin(x)", 0.0, 0.0),
            ("x^2", 3.0, 9.0),
            ("x**2", 3.0, 9.0),  # Python-style power should also work
            ("exp(x)", 0.0, 1.0),
            ("sqrt(x)", 4.0, 2.0),
            ("2*x + 1", 5.0, 11.0),
            ("2x + 1", 5.0, 11.0),  # implicit multiplication
        ],
    )
    def test_parses_and_evaluates_correctly(self, expression_parser, expression, test_point, expected):
        function_model = expression_parser.parse(expression)
        assert function_model.evaluate(test_point) == pytest.approx(expected, abs=1e-9)

    def test_source_text_preserved(self, expression_parser):
        function_model = expression_parser.parse("  sin(x)  ")
        assert function_model.source_text == "sin(x)"


class TestInvalidParsing:
    def test_empty_string_raises(self, expression_parser):
        with pytest.raises(ExpressionParsingError):
            expression_parser.parse("")

    def test_whitespace_only_raises(self, expression_parser):
        with pytest.raises(ExpressionParsingError):
            expression_parser.parse("   ")

    def test_unparseable_syntax_raises(self, expression_parser):
        with pytest.raises(ExpressionParsingError):
            expression_parser.parse("sin(x")  # unbalanced parenthesis

    def test_disallowed_variable_raises(self, expression_parser):
        with pytest.raises(ExpressionParsingError):
            expression_parser.parse("x + y")

    def test_error_message_names_the_bad_symbol(self, expression_parser):
        with pytest.raises(ExpressionParsingError, match="y"):
            expression_parser.parse("x + y")


class TestFunctionModelEvaluation:
    def test_division_by_zero_raises_domain_error(self, expression_parser):
        function_model = expression_parser.parse("1/x")
        with pytest.raises(IntegrationDomainError):
            function_model.evaluate(0.0)

    def test_sqrt_of_negative_raises_domain_error(self, expression_parser):
        function_model = expression_parser.parse("sqrt(x)")
        with pytest.raises(IntegrationDomainError):
            function_model.evaluate(-1.0)

    def test_derivative_of_x_squared_is_2x(self, expression_parser):
        function_model = expression_parser.parse("x^2")
        derivative = function_model.derivative(1)
        assert derivative.evaluate(3.0) == pytest.approx(6.0)

    def test_second_derivative_of_x_squared_is_constant_2(self, expression_parser):
        function_model = expression_parser.parse("x^2")
        second_derivative = function_model.derivative(2)
        assert second_derivative.evaluate(100.0) == pytest.approx(2.0)


class TestExactDefiniteIntegral:
    def test_exact_integral_of_x_squared(self, expression_parser):
        function_model = expression_parser.parse("x^2")
        exact = function_model.exact_definite_integral(0.0, 2.0)
        assert exact == pytest.approx(8.0 / 3.0)

    def test_exact_integral_of_sin(self, expression_parser):
        function_model = expression_parser.parse("sin(x)")
        exact = function_model.exact_definite_integral(0.0, 3.14159265358979)
        assert exact == pytest.approx(2.0, abs=1e-6)
