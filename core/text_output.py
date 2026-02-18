"""Clipboard and paste operations — degrades gracefully in headless mode."""

import logging
import sys
import time

logger = logging.getLogger(__name__)

_pyperclip = None
_pyautogui = None


def _get_pyperclip():
    global _pyperclip
    if _pyperclip is None:
        try:
            import pyperclip
            _pyperclip = pyperclip
        except ImportError:
            _pyperclip = False
            logger.debug("pyperclip not available (headless mode)")
    return _pyperclip if _pyperclip else None


def _get_pyautogui():
    global _pyautogui
    if _pyautogui is None:
        try:
            import pyautogui
            _pyautogui = pyautogui
        except ImportError:
            _pyautogui = False
            logger.debug("pyautogui not available (headless mode)")
    return _pyautogui if _pyautogui else None


def copy_to_clipboard(text: str):
    """Copy text to the system clipboard. No-op if pyperclip is unavailable."""
    pc = _get_pyperclip()
    if pc:
        pc.copy(text)
    else:
        logger.debug("Clipboard unavailable, skipping copy")


def paste_to_active_window(text: str):
    """Copy text to clipboard then simulate platform paste shortcut in the focused window."""
    pc = _get_pyperclip()
    pg = _get_pyautogui()
    if not pc or not pg:
        raise RuntimeError("paste_to_active_window requires a display (not available in headless mode)")
    pc.copy(text)
    time.sleep(0.05)
    pg.hotkey(*_paste_hotkey_keys())


def type_to_active_window(text: str, interval: float = 0.02):
    """Type text character-by-character into the currently focused window."""
    pg = _get_pyautogui()
    if not pg:
        raise RuntimeError("type_to_active_window requires a display (not available in headless mode)")
    pg.typewrite(text, interval=interval)


def _paste_hotkey_keys() -> tuple[str, str]:
    """Return the paste shortcut for the current platform."""
    if sys.platform == "darwin":
        return ("command", "v")
    return ("ctrl", "v")
