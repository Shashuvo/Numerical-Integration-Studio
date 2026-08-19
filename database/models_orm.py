"""
Row <-> object mapping helpers for the ``history`` table.

Kept separate from ``db_manager.py`` so serialization concerns
(JSON encoding of nested method results, datetime formatting) don't
clutter the connection/query logic, and so they can be unit-tested
in isolation without touching an actual database.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from models.history_entry import HistoryEntry, MethodResultSnapshot
from utils.exceptions import DatabaseError

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def history_entry_to_params(entry: HistoryEntry) -> tuple:
    """Convert a ``HistoryEntry`` into a parameter tuple for an INSERT.

    Args:
        entry: The history entry to serialize.

    Returns:
        A tuple ordered to match the INSERT statement's column list:
        (timestamp, function_expression, lower_limit, upper_limit,
        num_intervals, methods_json, results_json, exact_value, notes)
    """
    try:
        methods_json = json.dumps(entry.methods)
        results_json = json.dumps([r.to_dict() for r in entry.results])
    except (TypeError, ValueError) as exc:
        raise DatabaseError(
            f"Failed to serialize history entry to JSON: {exc}"
        ) from exc

    return (
        entry.timestamp.strftime(_TIMESTAMP_FORMAT),
        entry.function_expression,
        entry.lower_limit,
        entry.upper_limit,
        entry.num_intervals,
        methods_json,
        results_json,
        entry.exact_value,
        entry.notes,
    )


def row_to_history_entry(row: sqlite3.Row) -> HistoryEntry:
    """Convert a ``sqlite3.Row`` from the ``history`` table into a
    ``HistoryEntry`` instance.

    Args:
        row: A row fetched with ``row_factory = sqlite3.Row`` set on
            the connection, so columns are accessible by name.

    Returns:
        The reconstructed ``HistoryEntry``.

    Raises:
        DatabaseError: If the row's JSON columns are malformed, which
            would indicate external tampering or data corruption.
    """
    try:
        methods = json.loads(row["methods_json"])
        results_raw = json.loads(row["results_json"])
        results = [MethodResultSnapshot.from_dict(r) for r in results_raw]
        timestamp = datetime.strptime(row["timestamp"], _TIMESTAMP_FORMAT)
    except (TypeError, ValueError, KeyError) as exc:
        raise DatabaseError(
            f"Failed to deserialize history row (id={row['id']}): {exc}"
        ) from exc

    return HistoryEntry(
        id=row["id"],
        timestamp=timestamp,
        function_expression=row["function_expression"],
        lower_limit=row["lower_limit"],
        upper_limit=row["upper_limit"],
        num_intervals=row["num_intervals"],
        methods=methods,
        results=results,
        exact_value=row["exact_value"],
        notes=row["notes"],
    )
