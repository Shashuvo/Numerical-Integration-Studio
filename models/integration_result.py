"""
Data model representing the raw output of a single numerical
integration algorithm run, before error analysis is applied.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntegrationResult:
    """The raw result of running one algorithm once.

    This is the direct output of ``BaseAlgorithm.integrate()`` — it
    knows nothing about the exact value or errors. ``ErrorAnalysisService``
    (Module 7) combines this with an exact value to produce the richer
    ``MethodResultSnapshot`` used for display, storage, and reporting.

    Attributes:
        method_name: Canonical method key, e.g. "trapezoidal".
        approximate_value: The computed approximation of the integral.
        execution_time_seconds: Wall-clock time the computation took.
        lower_limit: Lower bound of integration used.
        upper_limit: Upper bound of integration used.
        num_intervals: Number of intervals (or steps) actually used.
            May differ from the user's requested value for methods that
            require an adjustment (documented per-algorithm).
    """

    method_name: str
    approximate_value: float
    execution_time_seconds: float
    lower_limit: float
    upper_limit: float
    num_intervals: int
