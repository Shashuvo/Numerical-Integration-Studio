"""
Loads and applies QSS stylesheets for light/dark theming.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PySide6.QtWidgets import QApplication

from utils.exceptions import ConfigurationError
from utils.logger import get_logger

ThemeName = Literal["light", "dark"]

_THEMES_DIR = Path(__file__).parent.parent / "resources" / "themes"


class ThemeService:
    """Loads QSS theme files and applies them to a running QApplication."""

    def __init__(self) -> None:
        self._logger = get_logger(__name__)
        self._current_theme: ThemeName = "light"

    @property
    def current_theme(self) -> ThemeName:
        """The name of the currently applied theme."""
        return self._current_theme

    def load_stylesheet(self, theme_name: ThemeName) -> str:
        """Read a QSS theme file from disk.

        Args:
            theme_name: Either "light" or "dark".

        Returns:
            The raw QSS content as a string.

        Raises:
            ConfigurationError: If the theme file cannot be found or read.
        """
        theme_path = _THEMES_DIR / f"{theme_name}.qss"
        try:
            return theme_path.read_text(encoding="utf-8")
        except OSError as exc:
            self._logger.exception("Failed to load theme file: %s", theme_path)
            raise ConfigurationError(
                f"Could not load '{theme_name}' theme from {theme_path}: {exc}"
            ) from exc

    def apply_theme(self, app: QApplication, theme_name: ThemeName) -> None:
        """Apply a theme to the whole application.

        Args:
            app: The running QApplication instance.
            theme_name: Either "light" or "dark".
        """
        stylesheet = self.load_stylesheet(theme_name)
        app.setStyleSheet(stylesheet)
        self._current_theme = theme_name
        self._logger.info("Applied '%s' theme", theme_name)
