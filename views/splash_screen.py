"""
Startup splash screen shown while the application initializes.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from utils.constants import APP_NAME, APP_VERSION


def _build_splash_pixmap(width: int = 480, height: int = 280) -> QPixmap:
    """Render a simple branded splash pixmap without requiring an image asset.

    Args:
        width: Pixmap width in pixels.
        height: Pixmap height in pixels.

    Returns:
        A ``QPixmap`` with the app name/version drawn on a solid background.
    """
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#1E2130"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(QColor("#8CA0F0"))
    title_font = painter.font()
    title_font.setPointSize(20)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.drawText(pixmap.rect().adjusted(20, 90, -20, 0), Qt.AlignmentFlag.AlignHCenter, APP_NAME)

    painter.setPen(QColor("#E4E6F0"))
    subtitle_font = painter.font()
    subtitle_font.setPointSize(10)
    subtitle_font.setBold(False)
    painter.setFont(subtitle_font)
    painter.drawText(
        pixmap.rect().adjusted(20, 130, -20, 0),
        Qt.AlignmentFlag.AlignHCenter,
        f"Version {APP_VERSION}",
    )

    painter.end()
    return pixmap


class AppSplashScreen(QSplashScreen):
    """A branded splash screen with progress-message support."""

    def __init__(self) -> None:
        super().__init__(_build_splash_pixmap())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def show_message(self, message: str) -> None:
        """Update the status text shown at the bottom of the splash screen.

        Args:
            message: A short status string, e.g. "Loading algorithms...".
        """
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            QColor("#B8BCD0"),
        )
        QApplication.processEvents()
