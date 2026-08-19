"""
SQLite persistence layer for calculation history.

``DatabaseManager`` is the single point of contact between the rest of
the application and the SQLite database. Controllers should depend on
an instance of this class (injected, not constructed ad hoc) so tests
can substitute an in-memory database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from database.models_orm import history_entry_to_params, row_to_history_entry
from models.history_entry import HistoryEntry
from utils.exceptions import DatabaseError
from utils.logger import get_logger

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

_INSERT_SQL = """
    INSERT INTO history (
        timestamp, function_expression, lower_limit, upper_limit,
        num_intervals, methods_json, results_json, exact_value, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_SELECT_ALL_SQL = "SELECT * FROM history ORDER BY timestamp DESC"
_SELECT_BY_ID_SQL = "SELECT * FROM history WHERE id = ?"
_DELETE_BY_ID_SQL = "DELETE FROM history WHERE id = ?"
_DELETE_ALL_SQL = "DELETE FROM history"


class DatabaseManager:
    """Manages the SQLite connection and all history CRUD operations.

    Args:
        db_path: Filesystem path to the SQLite database file. Parent
            directories are created automatically if missing. Pass
            ``":memory:"`` for an ephemeral, test-only database.

    Attributes:
        db_path: The resolved path (or ``:memory:``) backing this manager.
    """

    def __init__(self, db_path: str | Path = "data/history.db") -> None:
        self._logger = get_logger(__name__)
        self.db_path = str(db_path)

        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._initialize_schema()

    def _connect(self) -> None:
        """Open the SQLite connection with row access by column name."""
        try:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as exc:
            self._logger.exception("Failed to connect to database at %s", self.db_path)
            raise DatabaseError(
                f"Could not open database at '{self.db_path}': {exc}"
            ) from exc

    def _initialize_schema(self) -> None:
        """Apply schema.sql idempotently (safe to run on every startup)."""
        assert self._connection is not None
        try:
            schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
            self._connection.executescript(schema_sql)
            self._connection.commit()
            self._logger.info("Database schema initialized at %s", self.db_path)
        except (sqlite3.Error, OSError) as exc:
            self._logger.exception("Failed to initialize schema")
            raise DatabaseError(f"Could not initialize database schema: {exc}") from exc

    def insert_history_entry(self, entry: HistoryEntry) -> int:
        """Persist a new history entry.

        Args:
            entry: The entry to insert. ``entry.id`` is ignored (SQLite
                assigns the primary key).

        Returns:
            The auto-assigned primary key of the newly inserted row.

        Raises:
            DatabaseError: If serialization or the INSERT fails.
        """
        assert self._connection is not None
        params = history_entry_to_params(entry)
        try:
            cursor = self._connection.execute(_INSERT_SQL, params)
            self._connection.commit()
            new_id = cursor.lastrowid
            self._logger.info("Inserted history entry id=%s", new_id)
            return int(new_id)
        except sqlite3.Error as exc:
            self._connection.rollback()
            self._logger.exception("Failed to insert history entry")
            raise DatabaseError(f"Could not save calculation to history: {exc}") from exc

    def fetch_all_history(self) -> list[HistoryEntry]:
        """Retrieve every stored history entry, most recent first.

        Returns:
            A list of ``HistoryEntry`` objects (empty if none exist).

        Raises:
            DatabaseError: If the query or deserialization fails.
        """
        assert self._connection is not None
        try:
            rows = self._connection.execute(_SELECT_ALL_SQL).fetchall()
            return [row_to_history_entry(row) for row in rows]
        except sqlite3.Error as exc:
            self._logger.exception("Failed to fetch history")
            raise DatabaseError(f"Could not load calculation history: {exc}") from exc

    def fetch_history_by_id(self, entry_id: int) -> Optional[HistoryEntry]:
        """Retrieve a single history entry by its primary key.

        Args:
            entry_id: The ``id`` of the entry to retrieve.

        Returns:
            The matching ``HistoryEntry``, or ``None`` if no row has
            that id.

        Raises:
            DatabaseError: If the query or deserialization fails.
        """
        assert self._connection is not None
        try:
            row = self._connection.execute(_SELECT_BY_ID_SQL, (entry_id,)).fetchone()
            return row_to_history_entry(row) if row is not None else None
        except sqlite3.Error as exc:
            self._logger.exception("Failed to fetch history entry id=%s", entry_id)
            raise DatabaseError(f"Could not load history entry {entry_id}: {exc}") from exc

    def delete_history_entry(self, entry_id: int) -> bool:
        """Delete a single history entry.

        Args:
            entry_id: The ``id`` of the entry to delete.

        Returns:
            ``True`` if a row was deleted, ``False`` if no such id existed.

        Raises:
            DatabaseError: If the DELETE fails.
        """
        assert self._connection is not None
        try:
            cursor = self._connection.execute(_DELETE_BY_ID_SQL, (entry_id,))
            self._connection.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                self._logger.info("Deleted history entry id=%s", entry_id)
            return deleted
        except sqlite3.Error as exc:
            self._connection.rollback()
            self._logger.exception("Failed to delete history entry id=%s", entry_id)
            raise DatabaseError(f"Could not delete history entry {entry_id}: {exc}") from exc

    def clear_history(self) -> None:
        """Delete all history entries.

        Raises:
            DatabaseError: If the DELETE fails.
        """
        assert self._connection is not None
        try:
            self._connection.execute(_DELETE_ALL_SQL)
            self._connection.commit()
            self._logger.info("Cleared all history entries")
        except sqlite3.Error as exc:
            self._connection.rollback()
            self._logger.exception("Failed to clear history")
            raise DatabaseError(f"Could not clear calculation history: {exc}") from exc

    def close(self) -> None:
        """Close the underlying SQLite connection.

        Safe to call multiple times; subsequent calls are a no-op.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._logger.info("Database connection closed")

    def __enter__(self) -> "DatabaseManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
