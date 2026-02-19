from pynput import keyboard


DEFAULT_HOTKEY_LISTEN = "Ctrl+Alt+L"
DEFAULT_HOTKEY_RECORD = "Ctrl+Alt+R"
DEFAULT_HOTKEY_DIALOGUE = "Ctrl+Alt+D"

_MODIFIER_MAP = {
    "ctrl": "<ctrl>",
    "control": "<ctrl>",
    "alt": "<alt>",
    "shift": "<shift>",
    "cmd": "<cmd>",
    "win": "<cmd>",
    "super": "<cmd>",
}


class HotkeyManager:
    """Registers global hotkeys for toggling listening and recording modes."""

    def __init__(
        self,
        on_listen_toggle=None,
        on_record_toggle=None,
        on_dialogue_toggle=None,
        listen_hotkey: str = DEFAULT_HOTKEY_LISTEN,
        record_hotkey: str = DEFAULT_HOTKEY_RECORD,
        dialogue_hotkey: str = DEFAULT_HOTKEY_DIALOGUE,
    ):
        self.on_listen_toggle = on_listen_toggle
        self.on_record_toggle = on_record_toggle
        self.on_dialogue_toggle = on_dialogue_toggle
        self._listener = None
        self._running = False
        self._listen_hotkey = listen_hotkey
        self._record_hotkey = record_hotkey
        self._dialogue_hotkey = dialogue_hotkey

    def start(self):
        if self._running:
            return
        bindings = {
            _normalize_hotkey(self._listen_hotkey): self._trigger_listen,
            _normalize_hotkey(self._record_hotkey): self._trigger_record,
            _normalize_hotkey(self._dialogue_hotkey): self._trigger_dialogue,
        }
        self._listener = keyboard.GlobalHotKeys(bindings)
        self._listener.daemon = True
        self._listener.start()
        self._running = True

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._running = False

    def update_hotkeys(self, listen_hotkey: str, record_hotkey: str, dialogue_hotkey: str | None = None):
        # Validate before mutating the active listener.
        _normalize_hotkey(listen_hotkey)
        _normalize_hotkey(record_hotkey)
        if dialogue_hotkey:
            _normalize_hotkey(dialogue_hotkey)

        was_running = self._running
        if was_running:
            self.stop()
        self._listen_hotkey = listen_hotkey
        self._record_hotkey = record_hotkey
        if dialogue_hotkey:
            self._dialogue_hotkey = dialogue_hotkey
        if was_running:
            self.start()

    def get_hotkeys(self) -> tuple[str, str, str]:
        return self._listen_hotkey, self._record_hotkey, self._dialogue_hotkey

    def _trigger_listen(self):
        if self.on_listen_toggle:
            self.on_listen_toggle()

    def _trigger_record(self):
        if self.on_record_toggle:
            self.on_record_toggle()

    def _trigger_dialogue(self):
        if self.on_dialogue_toggle:
            self.on_dialogue_toggle()


def _normalize_hotkey(hotkey: str) -> str:
    if not hotkey or not isinstance(hotkey, str):
        raise ValueError("Hotkey must be a non-empty string.")

    parts = [p.strip().lower() for p in hotkey.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError("Use at least one modifier and one key (example: Ctrl+Alt+L).")

    normalized_parts = []
    for part in parts:
        mapped = _MODIFIER_MAP.get(part)
        if mapped:
            normalized_parts.append(mapped)
            continue
        if len(part) == 1 and part.isalnum():
            normalized_parts.append(part)
            continue
        raise ValueError(
            f"Unsupported key '{part}'. Use modifiers (Ctrl/Alt/Shift) plus a letter or digit."
        )

    if not any(p in {"<ctrl>", "<alt>", "<shift>", "<cmd>"} for p in normalized_parts):
        raise ValueError("Hotkey must include at least one modifier (Ctrl/Alt/Shift/Cmd).")

    if normalized_parts[-1].startswith("<"):
        raise ValueError("Hotkey must end with a non-modifier key.")

    return "+".join(normalized_parts)
