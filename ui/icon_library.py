"""Centralized UI icon lookup with asset-first fallback behavior."""

from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QStyle

from core.assets import asset_path


UI_ICON_FILES: dict[str, str] = {
    "tab_listening": "tab_listening.png",
    "tab_recording": "tab_recording.png",
    "tab_file": "tab_file.png",
    "tab_tts": "tab_tts.png",
    "tab_settings": "tab_settings.png",
    "output_minimize_tray": "output_minimize_tray.png",
    "output_edit": "output_edit.png",
    "output_clear": "output_clear.png",
    "output_copy": "output_copy.png",
    "settings_hotkeys_save": "settings_hotkeys_save.png",
    "settings_hotkeys_defaults": "settings_hotkeys_defaults.png",
    "settings_stt_save": "settings_stt_save.png",
    "settings_stt_defaults": "settings_stt_defaults.png",
    "settings_profile_apply": "settings_profile_apply.png",
    "settings_profile_save_new": "settings_profile_save_new.png",
    "settings_profile_update": "settings_profile_update.png",
    "settings_profile_delete": "settings_profile_delete.png",
    "settings_tts_save": "settings_tts_save.png",
    "settings_tts_defaults": "settings_tts_defaults.png",
    "tts_use_output": "tts_use_output.png",
    "tts_generate_play": "tts_generate_play.png",
    "tts_save_audio": "tts_save_audio.png",
    "listening_server_status": "listening_server_status.png",
    "listening_server_offline": "listening_server_offline.png",
    "listening_retry_last": "listening_retry_last.png",
}

UI_ICON_FALLBACKS: dict[str, QStyle.StandardPixmap] = {
    "tab_listening": QStyle.StandardPixmap.SP_MediaPlay,
    "tab_recording": QStyle.StandardPixmap.SP_DialogApplyButton,
    "tab_file": QStyle.StandardPixmap.SP_DirOpenIcon,
    "tab_tts": QStyle.StandardPixmap.SP_MediaVolume,
    "tab_settings": QStyle.StandardPixmap.SP_FileDialogDetailedView,
    "output_minimize_tray": QStyle.StandardPixmap.SP_TitleBarMinButton,
    "output_edit": QStyle.StandardPixmap.SP_FileDialogContentsView,
    "output_clear": QStyle.StandardPixmap.SP_TrashIcon,
    "output_copy": QStyle.StandardPixmap.SP_FileIcon,
    "settings_hotkeys_save": QStyle.StandardPixmap.SP_DialogSaveButton,
    "settings_hotkeys_defaults": QStyle.StandardPixmap.SP_BrowserReload,
    "settings_stt_save": QStyle.StandardPixmap.SP_DialogSaveButton,
    "settings_stt_defaults": QStyle.StandardPixmap.SP_BrowserReload,
    "settings_profile_apply": QStyle.StandardPixmap.SP_DialogApplyButton,
    "settings_profile_save_new": QStyle.StandardPixmap.SP_FileIcon,
    "settings_profile_update": QStyle.StandardPixmap.SP_BrowserReload,
    "settings_profile_delete": QStyle.StandardPixmap.SP_TrashIcon,
    "settings_tts_save": QStyle.StandardPixmap.SP_DialogSaveButton,
    "settings_tts_defaults": QStyle.StandardPixmap.SP_BrowserReload,
    "tts_use_output": QStyle.StandardPixmap.SP_ArrowDown,
    "tts_generate_play": QStyle.StandardPixmap.SP_MediaPlay,
    "tts_save_audio": QStyle.StandardPixmap.SP_DialogSaveButton,
    "listening_server_status": QStyle.StandardPixmap.SP_DriveNetIcon,
    "listening_server_offline": QStyle.StandardPixmap.SP_MessageBoxCritical,
    "listening_retry_last": QStyle.StandardPixmap.SP_BrowserReload,
}

_CACHE: dict[str, QIcon] = {}


def _icon_asset_path(icon_key: str) -> Path | None:
    name = UI_ICON_FILES.get(icon_key, "")
    return asset_path("icons", "ui", name) if name else None


def ui_icon(widget: QWidget, icon_key: str) -> QIcon:
    """Load branded icon from assets, or fall back to a native Qt icon."""
    cached = _CACHE.get(icon_key)
    if cached is not None:
        return cached

    path = _icon_asset_path(icon_key)
    if path is not None and path.exists():
        icon = QIcon(str(path))
        if not icon.isNull():
            _CACHE[icon_key] = icon
            return icon

    fallback = UI_ICON_FALLBACKS.get(icon_key)
    if fallback is not None:
        return widget.style().standardIcon(fallback)
    return QIcon()
