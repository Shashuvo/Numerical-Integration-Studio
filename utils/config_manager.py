"""
Loads and persists application settings to/from a YAML config file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from utils.constants import DEFAULT_CONFIG_PATH
from utils.exceptions import ConfigurationError
from utils.logger import get_logger

#: Settings applied when no config file exists yet, or when a file is
#: missing individual keys (e.g. after upgrading to a newer version
#: that added new settings).
DEFAULT_SETTINGS: dict[str, Any] = {
    "theme": "light",
    "decimal_precision": 8,
    "default_intervals": 100,
    "window_width": 1200,
    "window_height": 780,
    "database_path": "data/history.db",
}


class ConfigManager:
    """Reads and writes application settings from a YAML file on disk.

    On first use (no file present), a config file is created with
    ``DEFAULT_SETTINGS``. On subsequent loads, any keys missing from
    the file (e.g. because the application added new settings since
    it was last written) are backfilled from the defaults, so existing
    config files never cause a crash after an upgrade.
    """

    def __init__(self, config_path: str | Path = DEFAULT_CONFIG_PATH) -> None:
        self._logger = get_logger(__name__)
        self._config_path = Path(config_path)
        self._settings: dict[str, Any] = self._load_or_create()

    def _load_or_create(self) -> dict[str, Any]:
        """Load settings from disk, creating a default file if none exists.

        Returns:
            The merged settings dict (defaults backfilled for any
            missing keys).

        Raises:
            ConfigurationError: If the file exists but contains invalid YAML.
        """
        if not self._config_path.exists():
            self._logger.info("No config file found at %s; creating defaults", self._config_path)
            self._write(DEFAULT_SETTINGS)
            return dict(DEFAULT_SETTINGS)

        try:
            raw_text = self._config_path.read_text(encoding="utf-8")
            loaded = yaml.safe_load(raw_text) or {}
        except yaml.YAMLError as exc:
            self._logger.exception("Invalid YAML in config file %s", self._config_path)
            raise ConfigurationError(
                f"The settings file at '{self._config_path}' is corrupted or invalid: {exc}"
            ) from exc
        except OSError as exc:
            self._logger.exception("Failed to read config file %s", self._config_path)
            raise ConfigurationError(f"Could not read settings file: {exc}") from exc

        if not isinstance(loaded, dict):
            raise ConfigurationError(
                f"The settings file at '{self._config_path}' has an unexpected format."
            )

        merged = dict(DEFAULT_SETTINGS)
        merged.update(loaded)
        return merged

    def _write(self, settings: dict[str, Any]) -> None:
        """Persist ``settings`` to the config file.

        Args:
            settings: The full settings dict to write.

        Raises:
            ConfigurationError: If the file cannot be written.
        """
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with self._config_path.open("w", encoding="utf-8") as config_file:
                yaml.safe_dump(settings, config_file, default_flow_style=False, sort_keys=False)
        except OSError as exc:
            self._logger.exception("Failed to write config file %s", self._config_path)
            raise ConfigurationError(f"Could not save settings: {exc}") from exc

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for ``key``, or ``default`` if not present."""
        return self._settings.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Return a copy of all current settings."""
        return dict(self._settings)

    def set(self, key: str, value: Any) -> None:
        """Update a single setting and immediately persist all settings.

        Args:
            key: The setting name.
            value: The new value.
        """
        self._settings[key] = value
        self._write(self._settings)
        self._logger.info("Setting '%s' updated to %r", key, value)

    def update(self, updates: dict[str, Any]) -> None:
        """Update multiple settings at once and persist them.

        Args:
            updates: A dict of setting names to new values.
        """
        self._settings.update(updates)
        self._write(self._settings)
        self._logger.info("Settings updated: %s", ", ".join(updates.keys()))
