"""
Abstract base class defining the shared interface for all numerical
integration algorithms.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod

from models.function_model import FunctionModel
from models.integration_result import IntegrationResult


class BaseAlgorithm(ABC):
    """Interface every numerical integration method must implement.

    Subclasses implement ``_compute`` (the pure numerical work) and
    provide a ``method_key`` matching one of the canonical keys in
    ``utils.constants.ALL_METHODS``. The public ``integrate`` method
    wraps ``_compute`` with timing, so every algorithm reports its
    execution time consistently.
    """

    #: Canonical method key (see utils.constants). Must be overridden.
    method_key: str = ""

    def integrate(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> IntegrationResult:
        """Approximate the definite integral of ``function_model`` on [lower, upper].

        Args:
            function_model: The validated function to integrate.
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            num_intervals: Requested number of intervals/steps.

        Returns:
            An ``IntegrationResult`` with the approximation and timing.

        Raises:
            AlgorithmError: If ``num_intervals`` is unsuitable for this
                method (e.g. odd for Simpson's 1/3), or if the function
                is undefined at a required sample point.
        """
        start_time = time.perf_counter()
        approximate_value, actual_intervals = self._compute(
            function_model, lower, upper, num_intervals
        )
        elapsed = time.perf_counter() - start_time

        return IntegrationResult(
            method_name=self.method_key,
            approximate_value=approximate_value,
            execution_time_seconds=elapsed,
            lower_limit=lower,
            upper_limit=upper,
            num_intervals=actual_intervals,
        )

    @abstractmethod
    def _compute(
        self, function_model: FunctionModel, lower: float, upper: float, num_intervals: int
    ) -> tuple[float, int]:
        """Perform the actual numerical approximation.

        Args:
            function_model: The validated function to integrate.
            lower: Lower limit of integration.
            upper: Upper limit of integration.
            num_intervals: Requested number of intervals/steps.

        Returns:
            A tuple of (approximate_value, actual_num_intervals_used).
        """
        raise NotImplementedError
