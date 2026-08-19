"""
Centralized input validation rules for integration requests.
"""

from __future__ import annotations

from utils.constants import MAX_INTERVALS, MIN_INTERVALS
from utils.exceptions import ValidationError


class ValidationService:
    """Validates the numeric/structural parts of a compute request.

    Function syntax validation lives in ``ExpressionParserService``
    (it needs SymPy); this service covers everything else: limits,
    interval count, and method selection.
    """

    @staticmethod
    def validate_limits(lower: float, upper: float) -> None:
        """Ensure the lower limit is strictly less than the upper limit.

        Raises:
            ValidationError: If ``lower >= upper``.
        """
        if lower >= upper:
            raise ValidationError("The lower limit must be less than the upper limit.")

    @staticmethod
    def validate_num_intervals(num_intervals: int) -> None:
        """Ensure the interval count is within the supported range.

        Raises:
            ValidationError: If ``num_intervals`` is not a positive
                integer within [MIN_INTERVALS, MAX_INTERVALS].
        """
        if num_intervals < MIN_INTERVALS:
            raise ValidationError(
                f"Number of intervals must be at least {MIN_INTERVALS}. Got {num_intervals}."
            )
        if num_intervals > MAX_INTERVALS:
            raise ValidationError(
                f"Number of intervals must be at most {MAX_INTERVALS:,}. Got {num_intervals:,}."
            )

    @staticmethod
    def validate_methods_selected(methods: list[str]) -> None:
        """Ensure at least one integration method was selected.

        Raises:
            ValidationError: If ``methods`` is empty.
        """
        if not methods:
            raise ValidationError("Please select at least one integration method.")

    def validate_request(self, lower: float, upper: float, num_intervals: int, methods: list[str]) -> None:
        """Run all request-level validations in one call.

        Args:
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            num_intervals: Requested number of intervals.
            methods: Selected canonical method keys.

        Raises:
            ValidationError: If any individual check fails. The first
                failing check's message is raised.
        """
        self.validate_limits(lower, upper)
        self.validate_num_intervals(num_intervals)
        self.validate_methods_selected(methods)
