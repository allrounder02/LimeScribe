"""LemonFox Voice Transcriber — Entry Point"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from hotkeys import HotkeyManager


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    tray = TrayIcon()

    # Store tray reference so window can update icon states
    window.tray = tray

    # Tray menu actions
    tray.action_show.triggered.connect(window.show)
    tray.action_show.triggered.connect(window.raise_)
    tray.action_quit.triggered.connect(app.quit)

    tray.action_listen.triggered.connect(lambda: _tray_toggle_listen(window))
    tray.action_record.triggered.connect(lambda: _tray_toggle_record(window))

    # Double-click tray to show window
    tray.activated.connect(
        lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )

    # Global hotkeys (Ctrl+Alt+L = listen, Ctrl+Alt+R = record)
    hotkeys = HotkeyManager(
        on_listen_toggle=lambda: _tray_toggle_listen(window),
        on_record_toggle=lambda: _tray_toggle_record(window),
    )
    hotkeys.start()

    tray.show()
    window.show()

    ret = app.exec()
    hotkeys.stop()
    sys.exit(ret)


def _tray_toggle_listen(window):
    """Toggle listening mode from tray menu."""
    window.show()
    window.tabs.setCurrentIndex(0)  # Listening tab
    window.btn_listen_toggle.click()


def _tray_toggle_record(window):
    """Toggle recording from tray menu."""
    window.show()
    window.tabs.setCurrentIndex(1)  # Recording tab
    if window.recorder.recording:
        window._rec_stop()
    else:
        window._rec_start()


if __name__ == "__main__":
    main()
