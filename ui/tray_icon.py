from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction


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


class TrayIcon(QSystemTrayIcon):
    """System tray icon with context menu for the transcriber app."""

    def __init__(self, parent=None):
        # Build icons lazily after QApplication exists.
        self._icons = {
            "idle": _make_circle_icon("#888888"),
            "listening": _make_circle_icon("#ff3333"),
            "recording": _make_circle_icon("#ff3333"),
        }
        super().__init__(self._icons["idle"], parent)
        self.setToolTip("LemonFox Transcriber — Idle")
        self._build_menu()

    def _build_menu(self):
        menu = QMenu()
        self.action_show = QAction("Show Window")
        self.action_listen = QAction("Start Listening")
        self.action_record = QAction("Start Recording")
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
        self.setToolTip(f"LemonFox Transcriber — {labels.get(state, 'Idle')}")
