"""
Tests for DatabaseManager, database/models_orm.py, and HistoryEntry.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from database.db_manager import DatabaseManager
from models.history_entry import HistoryEntry, MethodResultSnapshot
from utils.exceptions import DatabaseError


def _make_entry(function_expression: str = "sin(x)") -> HistoryEntry:
    return HistoryEntry(
        function_expression=function_expression,
        lower_limit=0.0,
        upper_limit=3.14159,
        num_intervals=100,
        methods=["trapezoidal", "simpson_1_3"],
        results=[
            MethodResultSnapshot("trapezoidal", 0.9997, 1.0, 0.0003, 0.0003, 0.03, 0.0012),
            MethodResultSnapshot("simpson_1_3", 0.99999, 1.0, 0.00001, 0.00001, 0.001, 0.0018),
        ],
        exact_value=1.0,
        notes="test entry",
    )


class TestInsertAndFetch:
    def test_insert_returns_positive_id(self, db_manager):
        entry_id = db_manager.insert_history_entry(_make_entry())
        assert entry_id > 0

    def test_fetch_by_id_returns_matching_entry(self, db_manager):
        entry_id = db_manager.insert_history_entry(_make_entry("cos(x)"))
        fetched = db_manager.fetch_history_by_id(entry_id)
        assert fetched is not None
        assert fetched.function_expression == "cos(x)"
        assert fetched.num_intervals == 100
        assert fetched.methods == ["trapezoidal", "simpson_1_3"]
        assert len(fetched.results) == 2
        assert fetched.results[0].method_name == "trapezoidal"
        assert fetched.exact_value == pytest.approx(1.0)

    def test_fetch_by_nonexistent_id_returns_none(self, db_manager):
        assert db_manager.fetch_history_by_id(999999) is None

    def test_fetch_all_returns_all_entries_newest_first(self, db_manager):
        first_id = db_manager.insert_history_entry(_make_entry("first"))
        second_id = db_manager.insert_history_entry(_make_entry("second"))

        all_entries = db_manager.fetch_all_history()
        assert len(all_entries) == 2
        assert all_entries[0].id == second_id  # newest first
        assert all_entries[1].id == first_id

    def test_fetch_all_empty_database_returns_empty_list(self, db_manager):
        assert db_manager.fetch_all_history() == []


class TestDelete:
    def test_delete_existing_entry_returns_true(self, db_manager):
        entry_id = db_manager.insert_history_entry(_make_entry())
        assert db_manager.delete_history_entry(entry_id) is True
        assert db_manager.fetch_history_by_id(entry_id) is None

    def test_delete_nonexistent_entry_returns_false(self, db_manager):
        assert db_manager.delete_history_entry(999999) is False

    def test_clear_history_removes_everything(self, db_manager):
        db_manager.insert_history_entry(_make_entry("a"))
        db_manager.insert_history_entry(_make_entry("b"))
        db_manager.clear_history()
        assert db_manager.fetch_all_history() == []


class TestPersistence:
    def test_data_survives_reconnecting_to_same_file(self, tmp_path):
        db_path = tmp_path / "persist_test.db"

        manager_one = DatabaseManager(db_path)
        entry_id = manager_one.insert_history_entry(_make_entry("persisted_function"))
        manager_one.close()

        manager_two = DatabaseManager(db_path)
        fetched = manager_two.fetch_history_by_id(entry_id)
        assert fetched is not None
        assert fetched.function_expression == "persisted_function"
        manager_two.close()

    def test_schema_initialization_is_idempotent(self, tmp_path):
        db_path = tmp_path / "idempotent_test.db"
        DatabaseManager(db_path).close()
        # Opening a second time (schema already exists) must not raise.
        manager = DatabaseManager(db_path)
        assert manager.fetch_all_history() == []
        manager.close()


class TestContextManager:
    def test_with_statement_closes_connection(self, tmp_path):
        db_path = tmp_path / "context_test.db"
        with DatabaseManager(db_path) as manager:
            manager.insert_history_entry(_make_entry())
        # After the with-block, the connection should be closed.
        assert manager._connection is None


class TestHistoryEntryDefaults:
    def test_default_timestamp_is_timezone_aware_utc(self):
        entry = HistoryEntry(
            function_expression="x", lower_limit=0.0, upper_limit=1.0,
            num_intervals=10, methods=["trapezoidal"], results=[],
        )
        assert entry.timestamp.tzinfo is not None
        assert entry.timestamp.tzinfo == timezone.utc
