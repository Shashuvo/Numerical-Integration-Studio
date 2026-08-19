"""
Tests for ErrorAnalysisService.
"""

from __future__ import annotations

import pytest

from models.history_entry import MethodResultSnapshot
from models.integration_result import IntegrationResult


class TestComputeAbsoluteError:
    def test_known_difference(self, error_analysis_service):
        assert error_analysis_service.compute_absolute_error(1.05, 1.0) == pytest.approx(0.05)

    def test_none_when_exact_unknown(self, error_analysis_service):
        assert error_analysis_service.compute_absolute_error(1.05, None) is None

    def test_zero_when_exact_match(self, error_analysis_service):
        assert error_analysis_service.compute_absolute_error(2.0, 2.0) == 0.0


class TestComputeRelativeError:
    def test_known_ratio(self, error_analysis_service):
        assert error_analysis_service.compute_relative_error(1.1, 1.0) == pytest.approx(0.1)

    def test_none_when_exact_unknown(self, error_analysis_service):
        assert error_analysis_service.compute_relative_error(1.1, None) is None

    def test_none_when_exact_is_zero(self, error_analysis_service):
        # Division by zero would occur; must return None instead of raising.
        assert error_analysis_service.compute_relative_error(0.5, 0.0) is None


class TestComputePercentageError:
    def test_converts_fraction_to_percentage(self, error_analysis_service):
        assert error_analysis_service.compute_percentage_error(0.05) == pytest.approx(5.0)

    def test_none_passthrough(self, error_analysis_service):
        assert error_analysis_service.compute_percentage_error(None) is None


class TestBuildSnapshot:
    def test_full_snapshot_with_known_exact_value(self, error_analysis_service):
        result = IntegrationResult(
            method_name="trapezoidal", approximate_value=1.05,
            execution_time_seconds=0.001, lower_limit=0.0, upper_limit=1.0, num_intervals=10,
        )
        snapshot = error_analysis_service.build_snapshot(result, exact_value=1.0)

        assert snapshot.method_name == "trapezoidal"
        assert snapshot.approximate_value == 1.05
        assert snapshot.exact_value == 1.0
        assert snapshot.absolute_error == pytest.approx(0.05)
        assert snapshot.relative_error == pytest.approx(0.05)
        assert snapshot.percentage_error == pytest.approx(5.0)
        assert snapshot.execution_time_seconds == 0.001

    def test_snapshot_with_unknown_exact_value(self, error_analysis_service):
        result = IntegrationResult(
            method_name="taylor", approximate_value=2.71828,
            execution_time_seconds=0.002, lower_limit=0.0, upper_limit=1.0, num_intervals=10,
        )
        snapshot = error_analysis_service.build_snapshot(result, exact_value=None)

        assert snapshot.exact_value is None
        assert snapshot.absolute_error is None
        assert snapshot.relative_error is None
        assert snapshot.percentage_error is None


class TestFindBestMethodIndex:
    def _snapshot(self, method_name: str, absolute_error) -> MethodResultSnapshot:
        return MethodResultSnapshot(
            method_name=method_name, approximate_value=1.0, exact_value=1.0,
            absolute_error=absolute_error, relative_error=absolute_error,
            percentage_error=absolute_error, execution_time_seconds=0.001,
        )

    def test_picks_smallest_absolute_error(self, error_analysis_service):
        results = [
            self._snapshot("trapezoidal", 0.05),
            self._snapshot("simpson_1_3", 0.0001),
            self._snapshot("taylor", 0.001),
        ]
        assert error_analysis_service.find_best_method_index(results) == 1

    def test_none_when_no_errors_available(self, error_analysis_service):
        results = [self._snapshot("trapezoidal", None), self._snapshot("taylor", None)]
        assert error_analysis_service.find_best_method_index(results) is None

    def test_empty_list_returns_none(self, error_analysis_service):
        assert error_analysis_service.find_best_method_index([]) is None

    def test_skips_none_errors_among_mixed_results(self, error_analysis_service):
        results = [
            self._snapshot("trapezoidal", None),
            self._snapshot("simpson_1_3", 0.0002),
        ]
        assert error_analysis_service.find_best_method_index(results) == 1
