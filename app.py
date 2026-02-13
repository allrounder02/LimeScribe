"""LemonFox Voice Transcriber — Entry Point"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon
from hotkeys import HotkeyManager
from config import load_app_settings, save_app_settings, LOG_LEVEL, LOG_FILE


logger = logging.getLogger(__name__)


def _configure_logging():
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    handlers = [logging.StreamHandler()]
    if LOG_FILE:
        handlers.append(logging.FileHandler(LOG_FILE, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=handlers,
    )


def main():
    _configure_logging()
    logger.info("Starting LimeScribe")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    settings = load_app_settings()

    window = MainWindow()
    tray = TrayIcon()

    # Store tray reference so window can update icon states and menu labels
    window.attach_tray(tray)

    # Tray menu actions
    tray.action_show.triggered.connect(lambda: _show_window(window))
    tray.action_quit.triggered.connect(app.quit)

    tray.action_listen.triggered.connect(lambda: _tray_toggle_listen(window))
    tray.action_record.triggered.connect(lambda: _tray_toggle_record(window))

    # Double-click tray to show window
    tray.activated.connect(
        lambda reason: _show_window(window) if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )

    # Global hotkeys (Ctrl+Alt+L = listen, Ctrl+Alt+R = record)
    hotkeys = HotkeyManager(
        on_listen_toggle=lambda: _tray_toggle_listen(window),
        on_record_toggle=lambda: _tray_toggle_record(window),
        listen_hotkey=settings["hotkey_listen"],
        record_hotkey=settings["hotkey_record"],
    )
    window.attach_hotkey_manager(
        hotkeys,
        on_hotkeys_changed=lambda listen, record: _save_hotkey_settings(listen, record),
    )
    hotkeys.start()

    tray.show()
    window.show()

    ret = app.exec()
    hotkeys.stop()
    logger.info("Exiting LimeScribe")
    sys.exit(ret)


def _tray_toggle_listen(window):
    """Toggle listening mode from tray menu."""
    _show_window(window)
    window.tabs.setCurrentIndex(0)  # Listening tab
    window.btn_listen_toggle.click()


def _tray_toggle_record(window):
    """Toggle recording from tray menu."""
    _show_window(window)
    window.tabs.setCurrentIndex(1)  # Recording tab
    if window.recorder.recording:
        window._rec_stop()
    else:
        window._rec_start()


def _show_window(window):
    """Restore and focus the main window from tray/minimized states."""
    window.showNormal()
    window.raise_()
    window.activateWindow()


def _save_hotkey_settings(listen_hotkey: str, record_hotkey: str):
    save_app_settings(
        {
            "hotkey_listen": listen_hotkey,
            "hotkey_record": record_hotkey,
        }
    )


if __name__ == "__main__":
    main()
