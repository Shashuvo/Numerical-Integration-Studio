"""
Data model representing a single stored calculation history entry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class MethodResultSnapshot:
    """A lightweight, JSON-serializable snapshot of one method's result.

    This mirrors the fields of ``models.integration_result.IntegrationResult``
    but is intentionally decoupled from it so the database schema does not
    need to change if the richer runtime result model evolves.
    """

    method_name: str
    approximate_value: float
    exact_value: Optional[float]
    absolute_error: Optional[float]
    relative_error: Optional[float]
    percentage_error: Optional[float]
    execution_time_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize this snapshot to a plain dict (JSON-ready)."""
        return {
            "method_name": self.method_name,
            "approximate_value": self.approximate_value,
            "exact_value": self.exact_value,
            "absolute_error": self.absolute_error,
            "relative_error": self.relative_error,
            "percentage_error": self.percentage_error,
            "execution_time_seconds": self.execution_time_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MethodResultSnapshot":
        """Reconstruct a snapshot from a plain dict (as loaded from JSON)."""
        return cls(
            method_name=data["method_name"],
            approximate_value=data["approximate_value"],
            exact_value=data.get("exact_value"),
            absolute_error=data.get("absolute_error"),
            relative_error=data.get("relative_error"),
            percentage_error=data.get("percentage_error"),
            execution_time_seconds=data["execution_time_seconds"],
        )


@dataclass
class HistoryEntry:
    """A single row of calculation history.

    Attributes:
        id: Primary key. ``None`` for entries not yet persisted.
        timestamp: When the calculation was performed (UTC, ISO 8601).
        function_expression: The raw function string entered by the user,
            e.g. "sin(x) * exp(-x)".
        lower_limit: Lower bound of integration.
        upper_limit: Upper bound of integration.
        num_intervals: Number of intervals (or subdivisions) used.
        methods: Canonical method keys that were selected/run, e.g.
            ["trapezoidal", "simpson_1_3"].
        results: One ``MethodResultSnapshot`` per method in ``methods``.
        exact_value: The SymPy-computed exact value, if one could be found.
        notes: Optional free-text user annotation.
    """

    function_expression: str
    lower_limit: float
    upper_limit: float
    num_intervals: int
    methods: list[str]
    results: list[MethodResultSnapshot]
    id: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exact_value: Optional[float] = None
    notes: str = ""
