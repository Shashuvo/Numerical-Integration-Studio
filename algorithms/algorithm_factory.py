"""
Factory for constructing algorithm instances from canonical method keys.
"""

from __future__ import annotations

from algorithms.base_algorithm import BaseAlgorithm
from algorithms.simpson_one_third import SimpsonOneThirdRule
from algorithms.simpson_three_eighth import SimpsonThreeEighthRule
from algorithms.taylor_method import TaylorMethod
from algorithms.trapezoidal import TrapezoidalRule
from utils.constants import (
    METHOD_SIMPSON_1_3,
    METHOD_SIMPSON_3_8,
    METHOD_TAYLOR,
    METHOD_TRAPEZOIDAL,
)
from utils.exceptions import AlgorithmError

_REGISTRY: dict[str, type[BaseAlgorithm]] = {
    METHOD_TRAPEZOIDAL: TrapezoidalRule,
    METHOD_SIMPSON_1_3: SimpsonOneThirdRule,
    METHOD_SIMPSON_3_8: SimpsonThreeEighthRule,
    METHOD_TAYLOR: TaylorMethod,
}


class AlgorithmFactory:
    """Creates ``BaseAlgorithm`` instances by canonical method key.

    Using a factory (rather than if/elif chains in the controller) lets
    ``IntegrationController`` loop generically over selected methods:
    ``for key in request.methods: AlgorithmFactory.create(key).integrate(...)``.
    """

    @staticmethod
    def create(method_key: str) -> BaseAlgorithm:
        """Instantiate the algorithm registered under ``method_key``.

        Args:
            method_key: A canonical method key, e.g. "trapezoidal".

        Returns:
            A new instance of the corresponding algorithm class.

        Raises:
            AlgorithmError: If ``method_key`` is not a recognized method.
        """
        algorithm_class = _REGISTRY.get(method_key)
        if algorithm_class is None:
            known = ", ".join(sorted(_REGISTRY))
            raise AlgorithmError(
                f"Unknown integration method '{method_key}'. Known methods: {known}."
            )
        return algorithm_class()

    @staticmethod
    def available_methods() -> list[str]:
        """Return all canonical method keys this factory can construct."""
        return list(_REGISTRY.keys())
