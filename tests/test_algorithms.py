"""
Tests for the four numerical integration algorithms and the factory.
"""

from __future__ import annotations

import math

import pytest

from algorithms.algorithm_factory import AlgorithmFactory
from algorithms.simpson_one_third import SimpsonOneThirdRule
from algorithms.simpson_three_eighth import SimpsonThreeEighthRule
from algorithms.taylor_method import TaylorMethod
from algorithms.trapezoidal import TrapezoidalRule
from utils.exceptions import AlgorithmError, IntegrationDomainError

ALL_METHOD_KEYS = ("trapezoidal", "simpson_1_3", "simpson_3_8", "taylor")


class TestAlgorithmFactory:
    def test_creates_all_known_methods(self):
        for key in ALL_METHOD_KEYS:
            algorithm = AlgorithmFactory.create(key)
            assert algorithm.method_key == key

    def test_unknown_method_raises_algorithm_error(self):
        with pytest.raises(AlgorithmError):
            AlgorithmFactory.create("not_a_real_method")

    def test_available_methods_matches_known_keys(self):
        assert set(AlgorithmFactory.available_methods()) == set(ALL_METHOD_KEYS)


class TestKnownIntegrals:
    """Every method should approximate a simple polynomial well, and
    Simpson's rules / Taylor's method should be exact (to float
    precision) for polynomials within their respective exactness degree.
    """

    # Trapezoidal is only O(h^2)-accurate, so it needs a looser tolerance
    # at a modest n than the higher-order methods (which are near-exact
    # for a simple quadratic).
    _TOLERANCE_BY_METHOD = {
        "trapezoidal": 1e-3,
        "simpson_1_3": 1e-9,
        "simpson_3_8": 1e-9,
        "taylor": 1e-9,
    }

    @pytest.mark.parametrize("method_key", ALL_METHOD_KEYS)
    def test_x_squared_on_0_to_2(self, expression_parser, method_key):
        # exact = integral of x^2 from 0 to 2 = 8/3
        function_model = expression_parser.parse("x^2")
        algorithm = AlgorithmFactory.create(method_key)
        result = algorithm.integrate(function_model, 0.0, 2.0, 60)
        tolerance = self._TOLERANCE_BY_METHOD[method_key]
        assert result.approximate_value == pytest.approx(8.0 / 3.0, abs=tolerance)

    def test_simpson_1_3_exact_for_cubic(self, expression_parser):
        # Simpson's 1/3 is exact for polynomials up to degree 3.
        function_model = expression_parser.parse("x^3")
        algorithm = SimpsonOneThirdRule()
        result = algorithm.integrate(function_model, 0.0, 2.0, 10)
        assert result.approximate_value == pytest.approx(4.0, abs=1e-9)  # integral of x^3 on [0,2] = 4

    def test_trapezoidal_converges_at_second_order(self, expression_parser):
        # Trapezoidal error should shrink by ~4x when n doubles (O(h^2)).
        function_model = expression_parser.parse("x^2")
        algorithm = TrapezoidalRule()
        exact = 8.0 / 3.0

        error_n10 = abs(algorithm.integrate(function_model, 0.0, 2.0, 10).approximate_value - exact)
        error_n20 = abs(algorithm.integrate(function_model, 0.0, 2.0, 20).approximate_value - exact)

        assert error_n10 > 0  # sanity: trapezoidal is not exact for x^2
        ratio = error_n10 / error_n20
        assert ratio == pytest.approx(4.0, rel=0.05)


class TestSimpsonAutoAdjustment:
    """Simpson's rules must not fail on 'wrong-parity' n; they should
    auto-adjust and report the actual n used."""

    def test_simpson_1_3_adjusts_odd_n_to_even(self, expression_parser):
        function_model = expression_parser.parse("x^2")
        algorithm = SimpsonOneThirdRule()
        result = algorithm.integrate(function_model, 0.0, 2.0, 41)
        assert result.num_intervals == 42
        assert result.approximate_value == pytest.approx(8.0 / 3.0, abs=1e-6)

    def test_simpson_1_3_leaves_even_n_unchanged(self, expression_parser):
        function_model = expression_parser.parse("x^2")
        algorithm = SimpsonOneThirdRule()
        result = algorithm.integrate(function_model, 0.0, 2.0, 40)
        assert result.num_intervals == 40

    @pytest.mark.parametrize("requested,expected", [(40, 42), (41, 42), (42, 42), (43, 45)])
    def test_simpson_3_8_adjusts_to_next_multiple_of_3(self, expression_parser, requested, expected):
        function_model = expression_parser.parse("x^2")
        algorithm = SimpsonThreeEighthRule()
        result = algorithm.integrate(function_model, 0.0, 2.0, requested)
        assert result.num_intervals == expected
        assert result.approximate_value == pytest.approx(8.0 / 3.0, abs=1e-5)


class TestTaylorMethod:
    def test_exact_for_low_degree_polynomial(self, expression_parser):
        # Taylor's method (order 4) should be exact for x^2.
        function_model = expression_parser.parse("x^2")
        algorithm = TaylorMethod()
        result = algorithm.integrate(function_model, 0.0, 2.0, 20)
        assert result.approximate_value == pytest.approx(8.0 / 3.0, abs=1e-9)


class TestDomainErrors:
    def test_division_by_zero_raises_domain_error(self, expression_parser):
        function_model = expression_parser.parse("1/x")
        algorithm = TrapezoidalRule()
        # The interval [0, 1] includes x=0, where 1/x is undefined.
        with pytest.raises(IntegrationDomainError):
            algorithm.integrate(function_model, 0.0, 1.0, 10)

    def test_valid_domain_does_not_raise(self, expression_parser):
        function_model = expression_parser.parse("1/x")
        algorithm = TrapezoidalRule()
        # [1, 2] avoids the singularity at x=0.
        result = algorithm.integrate(function_model, 1.0, 2.0, 10)
        assert result.approximate_value == pytest.approx(math.log(2.0), abs=1e-2)


class TestExecutionTiming:
    def test_result_reports_nonnegative_execution_time(self, expression_parser):
        function_model = expression_parser.parse("sin(x)")
        algorithm = TrapezoidalRule()
        result = algorithm.integrate(function_model, 0.0, 3.14159, 10)
        assert result.execution_time_seconds >= 0.0
