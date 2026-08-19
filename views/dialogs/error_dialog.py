"""
Friendly, consistent error/warning/info message dialogs.

Centralizing these as module-level functions (rather than letting every
caller build its own ``QMessageBox``) keeps error presentation
consistent across the whole application.
"""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(parent: QWidget | None, title: str, message: str) -> None:
    """Display a modal error dialog.

    Args:
        parent: The parent widget (or None for a top-level dialog).
        title: The dialog's window title.
        message: The user-facing, friendly error description.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def show_warning(parent: QWidget | None, title: str, message: str) -> None:
    """Display a modal warning dialog.

    Args:
        parent: The parent widget (or None for a top-level dialog).
        title: The dialog's window title.
        message: The user-facing warning description.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def show_info(parent: QWidget | None, title: str, message: str) -> None:
    """Display a modal informational dialog.

    Args:
        parent: The parent widget (or None for a top-level dialog).
        title: The dialog's window title.
        message: The informational message to display.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()


def confirm_action(parent: QWidget | None, title: str, message: str) -> bool:
    """Display a Yes/No confirmation dialog.

    Args:
        parent: The parent widget (or None for a top-level dialog).
        title: The dialog's window title.
        message: The confirmation question to ask the user.

    Returns:
        True if the user chose "Yes", False otherwise.
    """
    result = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return result == QMessageBox.StandardButton.Yes
