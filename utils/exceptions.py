"""
Custom exception hierarchy for Numerical Integration Studio.

Using a dedicated hierarchy (rather than bare Exception / built-ins)
lets controllers and the UI layer catch specific failure categories
and present friendly, actionable error messages to the user.
"""

from __future__ import annotations


class NumericalIntegrationStudioError(Exception):
    """Base class for all application-specific exceptions."""


class ValidationError(NumericalIntegrationStudioError):
    """Raised when user-supplied input fails validation.

    Examples: invalid function syntax, lower limit >= upper limit,
    non-positive number of intervals, unsupported symbol in expression.
    """


class ExpressionParsingError(ValidationError):
    """Raised when a mathematical expression cannot be parsed by SymPy."""


class IntegrationDomainError(NumericalIntegrationStudioError):
    """Raised when a function is undefined somewhere on [a, b].

    Examples: division by zero, sqrt of a negative number, log of a
    non-positive number, encountered while sampling the integrand.
    """


class AlgorithmError(NumericalIntegrationStudioError):
    """Raised when a numerical integration algorithm fails to execute."""


class DatabaseError(NumericalIntegrationStudioError):
    """Raised when a SQLite operation fails (connection, schema, query)."""


class ReportGenerationError(NumericalIntegrationStudioError):
    """Raised when PDF or CSV report generation fails."""


class ConfigurationError(NumericalIntegrationStudioError):
    """Raised when the application configuration file is missing or invalid."""
