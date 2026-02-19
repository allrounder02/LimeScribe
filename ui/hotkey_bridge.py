"""Thread-safe bridge from background hotkey callbacks into Qt signals."""

from PyQt6.QtCore import QObject, pyqtSignal


class HotkeyBridge(QObject):
    """Emit Qt signals so UI actions run on the main Qt thread."""

    listen_requested = pyqtSignal()
    record_requested = pyqtSignal()
    dialogue_requested = pyqtSignal()

    def emit_listen_requested(self):
        self.listen_requested.emit()

    def emit_record_requested(self):
        self.record_requested.emit()

    def emit_dialogue_requested(self):
        self.dialogue_requested.emit()

