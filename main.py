"""
Application entry point for Numerical Integration Studio.

Startup sequence: configure logging -> show splash screen -> load
config -> connect to database -> build the main window -> apply the
saved theme -> wire everything together via MainController -> run.
"""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from controllers.main_controller import MainController
from database.db_manager import DatabaseManager
from services.theme_service import ThemeService
from utils.config_manager import ConfigManager
from utils.constants import APP_NAME, APP_VERSION, ORGANIZATION_NAME
from utils.exceptions import NumericalIntegrationStudioError
from utils.logger import configure_logging, get_logger
from views.dialogs.error_dialog import show_error
from views.main_window import MainWindow
from views.splash_screen import AppSplashScreen


def main() -> int:
    """Run the application. Returns the process exit code."""
    configure_logging(logging.INFO)
    logger = get_logger(__name__)
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORGANIZATION_NAME)

    splash = AppSplashScreen()
    splash.show()
    app.processEvents()

    try:
        splash.show_message("Loading configuration...")
        config_manager = ConfigManager()

        splash.show_message("Connecting to database...")
        database_manager = DatabaseManager(config_manager.get("database_path"))

        splash.show_message("Building interface...")
        window = MainWindow()
        window.resize(
            config_manager.get("window_width", 1200), config_manager.get("window_height", 780)
        )

        splash.show_message("Applying theme...")
        theme_service = ThemeService()
        theme_service.apply_theme(app, config_manager.get("theme", "light"))

        splash.show_message("Wiring application...")
        controller = MainController(app, window, config_manager, database_manager, theme_service)  # noqa: F841

    except NumericalIntegrationStudioError as exc:
        splash.close()
        logger.exception("Fatal error during startup")
        show_error(None, "Startup Error", f"{APP_NAME} could not start: {exc}")
        return 1

    splash.finish(window)
    window.show()

    exit_code = app.exec()

    database_manager.close()
    logger.info("%s exited with code %d", APP_NAME, exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
