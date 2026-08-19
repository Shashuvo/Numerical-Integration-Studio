"""
Generic embedded Matplotlib canvas with a navigation toolbar (zoom/pan).

This widget is intentionally content-agnostic: it exposes the raw
``Figure``/``Axes`` for callers (in ``plots/function_plotter.py`` and
``plots/convergence_plotter.py``) to draw onto, and a ``redraw()``
helper. Keeping plotting *logic* out of this widget lets it be reused
for both the function/approximation plot and the convergence plots.
"""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget


class PlotWidget(QWidget):
    """A reusable Matplotlib figure embedded in a Qt widget.

    Attributes:
        figure: The underlying Matplotlib ``Figure``.
        canvas: The Qt canvas rendering ``figure``.
        toolbar: The Matplotlib navigation toolbar (zoom, pan, save, etc.).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def clear(self) -> None:
        """Clear the figure entirely (all axes removed) and redraw."""
        self.figure.clear()
        self.canvas.draw_idle()

    def redraw(self) -> None:
        """Request a canvas redraw after external code has modified the figure."""
        self.canvas.draw_idle()

    def apply_theme_colors(self, is_dark: bool) -> None:
        """Adjust figure background/text colors to match the app theme.

        Args:
            is_dark: True to apply dark-theme-friendly colors, False for light.
        """
        face_color = "#232633" if is_dark else "#FFFFFF"
        text_color = "#E4E6F0" if is_dark else "#1E2130"

        self.figure.set_facecolor(face_color)
        for axis in self.figure.get_axes():
            axis.set_facecolor(face_color)
            axis.tick_params(colors=text_color)
            axis.xaxis.label.set_color(text_color)
            axis.yaxis.label.set_color(text_color)
            axis.title.set_color(text_color)
            for spine in axis.spines.values():
                spine.set_color(text_color)
        self.canvas.draw_idle()
