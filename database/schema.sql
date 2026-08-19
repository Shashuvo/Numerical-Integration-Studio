-- Numerical Integration Studio: SQLite schema
-- Applied automatically by DatabaseManager on first run.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS history (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT    NOT NULL,               -- ISO 8601 UTC
    function_expression TEXT    NOT NULL,
    lower_limit         REAL    NOT NULL,
    upper_limit         REAL    NOT NULL,
    num_intervals       INTEGER NOT NULL,
    methods_json        TEXT    NOT NULL,               -- JSON list[str]
    results_json        TEXT    NOT NULL,               -- JSON list[dict]
    exact_value         REAL,                           -- NULL if no closed form found
    notes               TEXT    NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_history_timestamp
    ON history (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_history_function
    ON history (function_expression);
