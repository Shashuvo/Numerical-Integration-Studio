"""
Shared pytest fixtures for the Numerical Integration Studio test suite.
"""

from __future__ import annotations

import os

# Must be set before any PySide6/Qt import happens, so the whole suite
# (including pytest-qt's own qapp fixture) runs headlessly in CI and
# other environments without a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pytest

# Allow `from algorithms.xxx import ...` etc. to resolve when pytest is
# run from the project root (this file's grandparent directory).
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from services.error_analysis_service import ErrorAnalysisService
from services.expression_parser import ExpressionParserService
from services.validation_service import ValidationService


@pytest.fixture
def expression_parser() -> ExpressionParserService:
    """A fresh ExpressionParserService for each test."""
    return ExpressionParserService()


@pytest.fixture
def error_analysis_service() -> ErrorAnalysisService:
    """A fresh ErrorAnalysisService for each test."""
    return ErrorAnalysisService()


@pytest.fixture
def validation_service() -> ValidationService:
    """A fresh ValidationService for each test."""
    return ValidationService()


@pytest.fixture
def db_manager(tmp_path):
    """A DatabaseManager backed by a temporary on-disk SQLite file.

    Using a real temp file (rather than ':memory:') also exercises the
    parent-directory-creation path in DatabaseManager.__init__.
    """
    manager = DatabaseManager(tmp_path / "test_history.db")
    yield manager
    manager.close()
