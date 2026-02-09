from pynput import keyboard


# Default hotkey combos
HOTKEY_LISTEN = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char("l")}
HOTKEY_RECORD = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char("r")}


class HotkeyManager:
    """Registers global hotkeys for toggling listening and recording modes."""

    def __init__(self, on_listen_toggle=None, on_record_toggle=None):
        self.on_listen_toggle = on_listen_toggle
        self.on_record_toggle = on_record_toggle
        self._current_keys = set()
        self._listener = None

    def start(self):
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        self._current_keys.add(key)

        if self._current_keys >= HOTKEY_LISTEN and self.on_listen_toggle:
            self.on_listen_toggle()
        elif self._current_keys >= HOTKEY_RECORD and self.on_record_toggle:
            self.on_record_toggle()

    def _on_release(self, key):
        self._current_keys.discard(key)
