"""
Aggregates the full outcome of a single "Compute" action.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.function_model import FunctionModel
from models.history_entry import MethodResultSnapshot
from models.integration_request import IntegrationRequest
from models.integration_result import IntegrationResult


@dataclass
class ComputationOutcome:
    """Everything produced by running one or more methods on one request.

    This is the object controllers pass around after a compute finishes:
    the view-update, history-save, and report-export steps all read from
    the same ``ComputationOutcome`` rather than recomputing anything.

    Attributes:
        function_model: The parsed function that was integrated.
        request: The original request (function text, limits, n, methods).
        raw_results: One raw ``IntegrationResult`` per method (used for
            plotting sample nodes).
        snapshots: One ``MethodResultSnapshot`` per method (used for
            display, history storage, and reports).
        exact_value: The SymPy-computed exact value, or None if no
            closed form could be found.
    """

    function_model: FunctionModel
    request: IntegrationRequest
    raw_results: list[IntegrationResult]
    snapshots: list[MethodResultSnapshot]
    exact_value: Optional[float]
