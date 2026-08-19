"""
Controller mediating between calculation outcomes and the history database.
"""

from __future__ import annotations

from database.db_manager import DatabaseManager
from models.comparison_model import ComputationOutcome
from models.history_entry import HistoryEntry
from utils.logger import get_logger


class HistoryController:
    """Saves computation outcomes to, and retrieves them from, SQLite history."""

    def __init__(self, database_manager: DatabaseManager) -> None:
        self._db = database_manager
        self._logger = get_logger(__name__)

    def save(self, outcome: ComputationOutcome, notes: str = "") -> int:
        """Persist a computation outcome as a new history entry.

        Args:
            outcome: The completed computation to save.
            notes: Optional free-text annotation.

        Returns:
            The new history entry's database id.

        Raises:
            DatabaseError: If the insert fails.
        """
        entry = HistoryEntry(
            function_expression=outcome.request.function_expression,
            lower_limit=outcome.request.lower_limit,
            upper_limit=outcome.request.upper_limit,
            num_intervals=outcome.request.num_intervals,
            methods=outcome.request.methods,
            results=outcome.snapshots,
            exact_value=outcome.exact_value,
            notes=notes,
        )
        return self._db.insert_history_entry(entry)

    def fetch_all(self) -> list[HistoryEntry]:
        """Return every stored history entry, most recent first.

        Raises:
            DatabaseError: If the query fails.
        """
        return self._db.fetch_all_history()

    def fetch_by_id(self, entry_id: int) -> HistoryEntry | None:
        """Return a single history entry, or None if it doesn't exist.

        Raises:
            DatabaseError: If the query fails.
        """
        return self._db.fetch_history_by_id(entry_id)

    def delete(self, entry_id: int) -> bool:
        """Delete a single history entry.

        Raises:
            DatabaseError: If the delete fails.
        """
        return self._db.delete_history_entry(entry_id)
