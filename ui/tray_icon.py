from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction

from core.assets import asset_path


def _make_circle_icon(color: str) -> QIcon:
    """Generate a simple colored circle icon for the tray."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(QColor(color).darker(120))
    painter.drawEllipse(4, 4, size - 8, size - 8)
    painter.end()
    return QIcon(pixmap)


def _select_logo_path() -> Path | None:
    for name in ("Zest_Voice_Logo_small.png", "Zest_Voice_Logo_transparent.png"):
        path = asset_path("icons", name)
        if path.exists():
            return path
    return None


def _make_logo_icon(path: Path | None, badge_color: str | None = None) -> QIcon:
    if path is None:
        return QIcon()

    source = QPixmap(str(path))
    if source.isNull():
        return QIcon()

    size = 64
    canvas = QPixmap(size, size)
    canvas.fill(QColor("transparent"))

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scaled = source.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)

    if badge_color:
        badge = QColor(badge_color)
        radius = 9
        painter.setBrush(badge)
        painter.setPen(badge.darker(130))
        painter.drawEllipse(size - (radius * 2) - 3, size - (radius * 2) - 3, radius * 2, radius * 2)

    painter.end()
    return QIcon(canvas)


class TrayIcon(QSystemTrayIcon):
    """System tray icon with context menu for the transcriber app."""

    def __init__(self, parent=None):
        logo_path = _select_logo_path()
        idle = _make_logo_icon(logo_path)
        listening = _make_logo_icon(logo_path, badge_color="#00c853")
        recording = _make_logo_icon(logo_path, badge_color="#ff1744")

        # Keep robust defaults if assets are missing or unreadable.
        self._icons = {
            "idle": idle if not idle.isNull() else _make_circle_icon("#888888"),
            "listening": listening if not listening.isNull() else _make_circle_icon("#2e7d32"),
            "recording": recording if not recording.isNull() else _make_circle_icon("#c62828"),
        }

        super().__init__(self._icons["idle"], parent)
        self.setToolTip("ZestVoice — Idle")
        self._build_menu()

    def _build_menu(self):
        menu = QMenu()
        self.action_show = QAction(self._icons["idle"], "Show Window")
        self.action_listen = QAction(self._icons["listening"], "Start Listening")
        self.action_record = QAction(self._icons["recording"], "Start Recording")
        self.action_quit = QAction("Quit")

        menu.addAction(self.action_show)
        menu.addSeparator()
        menu.addAction(self.action_listen)
        menu.addAction(self.action_record)
        menu.addSeparator()
        menu.addAction(self.action_quit)
        self.setContextMenu(menu)

    def set_state(self, state: str):
        """Update icon and tooltip. state: 'idle', 'listening', or 'recording'."""
        icon = self._icons.get(state, self._icons["idle"])
        self.setIcon(icon)
        labels = {"idle": "Idle", "listening": "Listening", "recording": "Recording"}
        self.setToolTip(f"ZestVoice — {labels.get(state, 'Idle')}")
