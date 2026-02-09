import time
import pyperclip
import pyautogui


def copy_to_clipboard(text: str):
    """Copy text to the system clipboard."""
    pyperclip.copy(text)


def paste_to_active_window(text: str):
    """Copy text to clipboard then simulate Ctrl+V in the currently focused window."""
    pyperclip.copy(text)
    time.sleep(0.05)  # small delay to ensure clipboard is set
    pyautogui.hotkey("ctrl", "v")


def type_to_active_window(text: str, interval: float = 0.02):
    """Type text character-by-character into the currently focused window."""
    pyautogui.typewrite(text, interval=interval)
