"""
Application-wide constants for Numerical Integration Studio.
"""

from __future__ import annotations

from pathlib import Path

APP_NAME = "Numerical Integration Studio"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "NIS"

# Filesystem locations (relative to the project root when run from source)
DATA_DIR = Path("data")
DEFAULT_DATABASE_PATH = DATA_DIR / "history.db"
DEFAULT_CONFIG_PATH = Path("config.yaml")
REPORTS_OUTPUT_DIR = Path("output") / "reports"
CSV_OUTPUT_DIR = Path("output") / "csv"

# Supported numerical integration methods (canonical names used as keys
# throughout the application: DB storage, factory lookups, UI labels)
METHOD_TRAPEZOIDAL = "trapezoidal"
METHOD_SIMPSON_1_3 = "simpson_1_3"
METHOD_SIMPSON_3_8 = "simpson_3_8"
METHOD_TAYLOR = "taylor"

ALL_METHODS = (
    METHOD_TRAPEZOIDAL,
    METHOD_SIMPSON_1_3,
    METHOD_SIMPSON_3_8,
    METHOD_TAYLOR,
)

PREDEFINED_EQUATIONS = {
    "sin(x)": {
        "expression": "sin(x)",
        "lower": 0.0,
        "upper": 3.141593,
        "intervals": 100,
    },
    "x**2": {
        "expression": "x**2",
        "lower": 0.0,
        "upper": 2.0,
        "intervals": 100,
    },
    "sqrt(x)": {
        "expression": "sqrt(x)",
        "lower": 0.0,
        "upper": 4.0,
        "intervals": 100,
    },
    "exp(-x)": {
        "expression": "exp(-x)",
        "lower": 0.0,
        "upper": 1.0,
        "intervals": 100,
    },
}

METHOD_DISPLAY_NAMES = {
    METHOD_TRAPEZOIDAL: "Trapezoidal Rule",
    METHOD_SIMPSON_1_3: "Simpson's 1/3 Rule",
    METHOD_SIMPSON_3_8: "Simpson's 3/8 Rule",
    METHOD_TAYLOR: "Taylor's Method",
}

# Validation limits
MIN_INTERVALS = 1
MAX_INTERVALS = 1_000_000
