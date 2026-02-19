"""GUI runtime bootstrap and wiring for ZestVoice."""

import logging
import sys
from collections.abc import Sequence

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

from config import LOG_FILE, LOG_LEVEL, load_app_settings, save_app_settings
from core.app_config import AppConfig
from core.assets import asset_path
from core.http_client import close_shared_client
from hotkeys import HotkeyManager
from ui.hotkey_bridge import HotkeyBridge
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon

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


def _load_app_icon() -> QIcon:
    for name in ("Zest_Voice_Logo_small.png", "Zest_Voice_Logo_transparent.png"):
        icon = QIcon(str(asset_path("icons", name)))
        if not icon.isNull():
            return icon
    return QIcon()


def _load_taskbar_icon() -> QIcon:
    """Build a multi-size icon for crisp taskbar rendering."""
    icon = QIcon()
    source = None
    for name in ("Zest_Voice_Logo_small.png", "Zest_Voice_Logo_transparent.png"):
        path = asset_path("icons", name)
        if path.exists():
            source = str(path)
            break
    if source:
        for size in (16, 20, 24, 32, 40, 48, 64, 128, 256):
            icon.addFile(source, QSize(size, size))
    return icon if not icon.isNull() else _load_app_icon()


def _configure_windows_taskbar_identity():
    """Ensure Windows groups this app under ZestVoice with its own taskbar icon."""
    if not sys.platform.startswith("win"):
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ZestVoice.App")
    except Exception as e:
        logger.debug("Unable to set Windows AppUserModelID: %s", e)


def _wire_tray(tray: TrayIcon, window: MainWindow, app: QApplication):
    tray.action_show.triggered.connect(window.show_and_focus)
    tray.action_quit.triggered.connect(app.quit)
    tray.action_listen.triggered.connect(window.toggle_listening_from_external)
    tray.action_record.triggered.connect(window.toggle_recording_from_external)
    tray.activated.connect(
        lambda reason: window.show_and_focus() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
    )


def _wire_settings(window: MainWindow, hotkeys: HotkeyManager, settings: dict):
    window.attach_hotkey_manager(
        hotkeys,
        on_hotkeys_changed=lambda listen, record: save_app_settings(
            {
                "hotkey_listen": listen,
                "hotkey_record": record,
            }
        ),
    )
    window.attach_stt_settings(settings, on_stt_settings_changed=save_app_settings)
    window.attach_tts_settings(settings, on_tts_settings_changed=save_app_settings)
    window.attach_dialogue_settings(settings, on_dialogue_settings_changed=save_app_settings)
    window.attach_profiles(settings, on_profiles_changed=save_app_settings)
    window.attach_tts_profiles(settings, on_tts_profiles_changed=save_app_settings)
    window.attach_ui_settings(settings, on_ui_settings_changed=save_app_settings)


def _build_hotkeys(window: MainWindow, settings: dict) -> HotkeyManager:
    # pynput runs callbacks on a background thread; bridge to Qt signals first.
    bridge = HotkeyBridge(parent=window)
    bridge.listen_requested.connect(window.toggle_listening_from_external)
    bridge.record_requested.connect(window.toggle_recording_from_external)
    bridge.dialogue_requested.connect(window.toggle_voice_dialogue_from_external)
    return HotkeyManager(
        on_listen_toggle=bridge.emit_listen_requested,
        on_record_toggle=bridge.emit_record_requested,
        on_dialogue_toggle=bridge.emit_dialogue_requested,
        listen_hotkey=settings["hotkey_listen"],
        record_hotkey=settings["hotkey_record"],
        dialogue_hotkey=settings.get("hotkey_dialogue", "Ctrl+Alt+D"),
    )


def run_gui_app(argv: Sequence[str] | None = None) -> int:
    _configure_logging()
    logger.info("Starting ZestVoice")

    qt_argv = list(argv) if argv is not None else sys.argv
    app = QApplication(qt_argv)
    _configure_windows_taskbar_identity()

    app_icon = _load_taskbar_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    app.setQuitOnLastWindowClosed(False)

    config = AppConfig.from_env()
    settings = load_app_settings()

    window = MainWindow(config=config)
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    tray = TrayIcon()
    window.attach_tray(tray)

    _wire_tray(tray, window, app)

    hotkeys = _build_hotkeys(window, settings)
    _wire_settings(window, hotkeys, settings)
    try:
        hotkeys.start()
        tray.show()
        window.show()
        return app.exec()
    finally:
        hotkeys.stop()
        close_shared_client()
        logger.info("Exiting ZestVoice")
