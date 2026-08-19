"""
Data model representing a single "compute" request from the user.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrationRequest:
    """Everything needed to run one or more integration methods.

    Attributes:
        function_expression: The raw function string, e.g. "sin(x)".
        lower_limit: Lower bound of integration (a).
        upper_limit: Upper bound of integration (b).
        num_intervals: Requested number of intervals (n).
        methods: Canonical method keys to run, e.g.
            ["trapezoidal", "simpson_1_3"].
    """

    function_expression: str
    lower_limit: float
    upper_limit: float
    num_intervals: int
    methods: list[str]
