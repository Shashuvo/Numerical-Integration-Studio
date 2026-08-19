"""
Tests for ValidationService.
"""

from __future__ import annotations

import pytest

from utils.constants import MAX_INTERVALS, MIN_INTERVALS
from utils.exceptions import ValidationError


class TestValidateLimits:
    def test_valid_limits_do_not_raise(self, validation_service):
        validation_service.validate_limits(0.0, 1.0)  # should not raise

    def test_equal_limits_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_limits(1.0, 1.0)

    def test_reversed_limits_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_limits(5.0, 0.0)

    def test_negative_limits_are_valid_if_ordered(self, validation_service):
        validation_service.validate_limits(-10.0, -5.0)  # should not raise


class TestValidateNumIntervals:
    def test_minimum_valid_value(self, validation_service):
        validation_service.validate_num_intervals(MIN_INTERVALS)  # should not raise

    def test_maximum_valid_value(self, validation_service):
        validation_service.validate_num_intervals(MAX_INTERVALS)  # should not raise

    def test_zero_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_num_intervals(0)

    def test_negative_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_num_intervals(-5)

    def test_exceeding_maximum_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_num_intervals(MAX_INTERVALS + 1)


class TestValidateMethodsSelected:
    def test_at_least_one_method_does_not_raise(self, validation_service):
        validation_service.validate_methods_selected(["trapezoidal"])  # should not raise

    def test_empty_list_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_methods_selected([])


class TestValidateRequest:
    def test_all_valid_does_not_raise(self, validation_service):
        validation_service.validate_request(0.0, 1.0, 100, ["trapezoidal"])  # should not raise

    def test_bad_limits_raises_before_other_checks(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_request(1.0, 0.0, 100, ["trapezoidal"])

    def test_bad_intervals_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_request(0.0, 1.0, -1, ["trapezoidal"])

    def test_no_methods_raises(self, validation_service):
        with pytest.raises(ValidationError):
            validation_service.validate_request(0.0, 1.0, 100, [])
