"""Main application window — coordinates services and UI panels."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QToolButton, QFileDialog, QApplication,
    QSystemTrayIcon, QSplitter, QSizePolicy, QGroupBox,
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal

from core.app_config import AppConfig
from core.audio_format import detect_audio_format
from core.dialogue_service import DialogueService
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService
from core.text_output import copy_to_clipboard
from core.voice_dialogue import VoiceDialogueOrchestrator, VoiceDialogueState
from core.wav_playback import WavPlaybackController
from ui.dialogue_panel import DialoguePanel
from ui.icon_library import ui_icon
from ui.tts_panel import TTSPanel
from ui.settings_panel import SettingsPanel

logger = logging.getLogger(__name__)
OUTPUT_HISTORY_LIMIT = 3
OUTPUT_HISTORY_PREVIEW_CHARS = 40


class MainWindow(QMainWindow):
    """Main application window with Capture / TTS / Dialogue / Settings tabs."""

    # Signals for thread-safe service callbacks
    _transcription_ready = pyqtSignal(str)
    _transcription_error = pyqtSignal(str)
    _tts_audio_ready = pyqtSignal(bytes)
    _tts_error = pyqtSignal(str)
    _dialogue_reply = pyqtSignal(str)
    _dialogue_error = pyqtSignal(str)
    _voice_state_changed = pyqtSignal(str)
    _voice_user_transcript = pyqtSignal(str)
    _voice_assistant_text = pyqtSignal(str)
    _voice_error = pyqtSignal(str)
    _voice_turn_complete = pyqtSignal()

    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__()
        self.setWindowTitle("LemonFox Transcriber")
        self.setMinimumHeight(480)
        self.resize(980, 680)

        self._config = config or AppConfig.from_env()

        # Services (no PyQt6 dependency in core layer)
        self.stt_service = TranscriptionService(
            config=self._config,
            on_transcription=self._transcription_ready.emit,
            on_error=self._transcription_error.emit,
        )
        self.tts_service = TTSService(
            config=self._config,
            on_audio_ready=self._tts_audio_ready.emit,
            on_error=self._tts_error.emit,
        )
        self.dialogue_service = DialogueService(
            config=self._config,
            on_reply=self._dialogue_reply.emit,
            on_error=self._dialogue_error.emit,
        )
        self.tts_playback = WavPlaybackController()
        self._tts_ui_timer = QTimer(self)
        self._tts_ui_timer.setInterval(120)
        self._tts_ui_timer.timeout.connect(self._refresh_tts_playback_ui)

        # Connect signals to UI handlers (runs on main thread)
        self.voice_dialogue = VoiceDialogueOrchestrator(
            config=self._config,
            dialogue_service=self.dialogue_service,
            on_state_changed=self._voice_state_changed.emit,
            on_user_transcript=self._voice_user_transcript.emit,
            on_assistant_text=self._voice_assistant_text.emit,
            on_error=self._voice_error.emit,
            on_turn_complete=self._voice_turn_complete.emit,
        )

        self._transcription_ready.connect(self._on_transcription_done)
        self._transcription_error.connect(self._on_transcription_error)
        self._tts_audio_ready.connect(self._on_tts_done_play)
        self._tts_error.connect(self._on_tts_error)
        self._dialogue_reply.connect(self._on_dialogue_reply)
        self._dialogue_error.connect(self._on_dialogue_error)
        self._voice_state_changed.connect(self._on_voice_state_changed)
        self._voice_user_transcript.connect(self._on_voice_user_transcript)
        self._voice_assistant_text.connect(self._on_voice_assistant_text)
        self._voice_error.connect(self._on_voice_error)
        self._voice_turn_complete.connect(self._on_voice_turn_complete)

        self.tray = None
        self._on_hotkeys_changed = None
        self._on_stt_settings_changed = None
        self._on_tts_settings_changed = None
        self._on_dialogue_settings_changed = None
        self._on_profiles_changed = None
        self._on_tts_profiles_changed = None
        self._on_ui_settings_changed = None
        self.auto_copy_transcription = True
        self.clear_output_after_copy = False
        self.stop_listening_after_copy = False
        self.keep_wrapping_parentheses = False
        self.dark_mode = False
        self._server_online = True
        self._profiles = []
        self._updating_listening_profiles = False
        self._tts_profiles = []
        self._output_history = []
        self._tts_last_audio_dir = ""

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Vertical splitter so output panel can be resized
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(True)
        self.main_splitter.setHandleWidth(8)
        layout.addWidget(self.main_splitter)
        self.main_splitter.splitterMoved.connect(self._on_splitter_moved)

        # Tabs (top pane)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_capture_tab(), "Capture")
        self.tabs.setTabIcon(0, ui_icon(self, "tab_listening"))

        # TTS panel (extracted widget)
        self.tts_panel = TTSPanel()
        self.tts_panel.generate_requested.connect(self._on_tts_generate)
        self.tts_panel.optimization_settings_changed.connect(self._on_tts_optimization_settings_changed)
        self.tts_panel.use_output_requested.connect(self._load_tts_from_output)
        self.tts_panel.save_audio_requested.connect(self._save_last_tts_audio)
        self.tts_panel.open_saved_audio_requested.connect(self._open_saved_tts_audio)
        self.tts_panel.tts_profile_selected.connect(self._on_tts_profile_selected)
        self.tts_panel.play_pause_requested.connect(self._toggle_tts_playback)
        self.tts_panel.stop_requested.connect(self._stop_tts_playback)
        self.tts_panel.seek_requested.connect(self._seek_tts_playback)
        self.tts_panel.speed_changed.connect(self._set_tts_playback_speed)
        self.tts_panel.pitch_changed.connect(self._set_tts_playback_pitch)
        self.tts_panel.api_speed_changed.connect(self._on_tts_api_speed_changed)
        self.tabs.addTab(self.tts_panel, "Text to Speech")
        self.tabs.setTabIcon(1, ui_icon(self, "tab_tts"))

        # Dialogue panel (OpenAI-compatible chat)
        self.dialogue_panel = DialoguePanel()
        self.dialogue_panel.send_requested.connect(self._on_dialogue_send)
        self.dialogue_panel.reset_requested.connect(self._on_dialogue_reset)
        self.dialogue_panel.use_output_requested.connect(self._load_dialogue_from_output)
        self.dialogue_panel.model_changed.connect(self._on_dialogue_model_changed)
        self.dialogue_panel.system_prompt_changed.connect(self._on_dialogue_system_prompt_changed)
        self.dialogue_panel.history_mode_changed.connect(self._on_dialogue_history_mode_changed)
        self.dialogue_panel.voice_start_requested.connect(self._on_voice_start)
        self.dialogue_panel.voice_stop_requested.connect(self._on_voice_stop)
        self.dialogue_panel.auto_listen_changed.connect(self._on_voice_auto_listen_changed)
        self.dialogue_panel.set_model(self.dialogue_service.client.model, emit=False)
        self.dialogue_panel.set_system_prompt(self.dialogue_service.system_prompt, emit=False)
        self.dialogue_panel.set_include_history(self.dialogue_service.include_history, emit=False)
        self.tabs.addTab(self.dialogue_panel, "Dialogue")
        self.tabs.setTabIcon(2, ui_icon(self, "tab_dialogue"))

        # Settings panel (extracted widget)
        self.settings_panel = SettingsPanel()
        self.settings_panel.hotkeys_save_requested.connect(self._on_hotkeys_saved)
        self.settings_panel.stt_settings_changed.connect(self._on_stt_settings_from_panel)
        self.settings_panel.tts_settings_changed.connect(self._on_tts_settings_from_panel)
        self.settings_panel.profiles_changed.connect(self._on_profiles_from_panel)
        self.settings_panel.tts_profiles_changed.connect(self._on_tts_profiles_from_panel)
        self.settings_panel.ui_settings_changed.connect(self._on_ui_settings_from_panel)
        self.tabs.addTab(self.settings_panel, "Settings")
        self.tabs.setTabIcon(3, ui_icon(self, "tab_settings"))

        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.tabs.setMinimumHeight(100)
        self.main_splitter.addWidget(self.tabs)

        # Shared output area (bottom pane)
        self.main_splitter.addWidget(self._build_output_panel())
        self.main_splitter.setStretchFactor(0, 2)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setCollapsible(0, True)
        self.main_splitter.setCollapsible(1, True)

        self._apply_theme()
        self.statusBar().showMessage("Ready")

    # ── Output panel ───────────────────────────────────────────────

    def _build_output_panel(self):
        panel = QWidget()
        panel.setMinimumHeight(120)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.output_label = QLabel("Transcription Output:")
        layout.addWidget(self.output_label)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(False)
        self.text_output.setPlaceholderText("Transcription output appears here. You can edit it directly.")
        layout.addWidget(self.text_output)

        history_row = QHBoxLayout()
        history_row.addWidget(QLabel("Recent outputs:"))
        self.combo_output_history = QComboBox()
        self.combo_output_history.setEditable(False)
        self.combo_output_history.setMinimumContentsLength(26)
        self.combo_output_history.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.btn_restore_output = QPushButton("Restore")
        self.btn_restore_output.clicked.connect(self._restore_selected_output)
        history_row.addWidget(self.combo_output_history, 1)
        history_row.addWidget(self.btn_restore_output)
        layout.addLayout(history_row)

        btn_row = QHBoxLayout()
        self.btn_quick_listen = QPushButton("Listen")
        self.btn_quick_listen.clicked.connect(self._toggle_quick_listening)
        self.btn_quick_listen.setIcon(ui_icon(self, "tab_listening"))
        self.btn_quick_listen.setToolTip("Start/stop listening mode")
        self.btn_edit_output = QPushButton("Edit Output")
        self.btn_edit_output.clicked.connect(self._focus_output_for_edit)
        self.btn_edit_output.setIcon(ui_icon(self, "output_edit"))
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self._clear_output)
        self.btn_clear.setIcon(ui_icon(self, "output_clear"))
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy_output)
        self.btn_copy.setIcon(ui_icon(self, "output_copy"))
        self._sync_quick_listen_button(self.stt_service.is_listening())
        self._refresh_output_history_controls()
        btn_row.addWidget(self.btn_quick_listen)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_edit_output)
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_copy)
        layout.addLayout(btn_row)
        return panel

    # ── Attach methods (called by app.py) ─────────────────────────

    def attach_tray(self, tray):
        self.tray = tray
        self._sync_listening_ui(self.btn_listen_toggle.isChecked())

    def attach_hotkey_manager(self, hotkeys, on_hotkeys_changed=None):
        self._on_hotkeys_changed = on_hotkeys_changed
        listen_hotkey, record_hotkey, _dialogue_hotkey = hotkeys.get_hotkeys()
        self.settings_panel.attach_hotkey_manager(hotkeys, listen_hotkey, record_hotkey)

    def attach_stt_settings(self, settings: dict, on_stt_settings_changed=None):
        self._on_stt_settings_changed = on_stt_settings_changed
        self.settings_panel.apply_stt_settings(
            language=settings.get("stt_language", self.stt_service.client.language),
            response_format=settings.get("stt_response_format", self.stt_service.client.response_format),
            auto_copy=bool(settings.get("auto_copy_transcription", True)),
            clear_output_after_copy=bool(settings.get("clear_output_after_copy", False)),
            stop_listening_after_copy=bool(settings.get("stop_listening_after_copy", False)),
            keep_wrapping_parentheses=bool(settings.get("keep_wrapping_parentheses", False)),
            vad_noise_level=settings.get("vad_noise_level", None),
            vad_aggressiveness=settings.get("vad_aggressiveness", self.stt_service.config.vad_aggressiveness),
            vad_min_speech_seconds=settings.get(
                "vad_min_speech_seconds", self.stt_service.config.vad_min_speech_seconds
            ),
        )

    def attach_tts_settings(self, settings: dict, on_tts_settings_changed=None):
        self._on_tts_settings_changed = on_tts_settings_changed
        self.settings_panel.apply_tts_settings(
            model=settings.get("tts_model", self.tts_service.client.model),
            voice=settings.get("tts_voice", self.tts_service.client.voice),
            language=settings.get("tts_language", self.tts_service.client.language),
            response_format=settings.get("tts_response_format", self.tts_service.client.response_format),
            speed=str(settings.get("tts_speed", self.tts_service.client.speed)),
        )
        self.tts_panel.set_api_speed(self._coerce_tts_speed_value(settings.get("tts_speed", self.tts_service.client.speed)) or 1.0)
        threshold_raw = settings.get("tts_optimize_threshold_chars", 240)
        try:
            threshold_chars = int(threshold_raw)
        except (TypeError, ValueError):
            threshold_chars = 240
        self.tts_panel.set_long_text_optimization(
            enabled=bool(settings.get("tts_optimize_long_text", True)),
            threshold_chars=threshold_chars,
            emit=False,
        )

    def attach_dialogue_settings(self, settings: dict, on_dialogue_settings_changed=None):
        self._on_dialogue_settings_changed = on_dialogue_settings_changed
        model = str(settings.get("chat_model", self.dialogue_service.client.model)).strip()
        system_prompt = str(settings.get("chat_system_prompt", self.dialogue_service.system_prompt)).strip()
        include_history = bool(settings.get("chat_include_history", True))

        self.dialogue_panel.set_model(model, emit=False)
        self.dialogue_panel.set_system_prompt(system_prompt, emit=False)
        self.dialogue_panel.set_include_history(include_history, emit=False)
        self.dialogue_service.update_settings(
            model=model,
            system_prompt=system_prompt,
            include_history=include_history,
            reset_history=True,
        )

    def attach_profiles(self, settings: dict, on_profiles_changed=None):
        self._on_profiles_changed = on_profiles_changed
        profiles = settings.get("profiles", [])
        self._profiles = [
            dict(p)
            for p in profiles
            if isinstance(p, dict) and isinstance(p.get("name"), str) and p["name"].strip()
        ]
        if not self._profiles:
            self._profiles = [
                {
                    "name": "Default",
                    "stt_language": self.stt_service.client.language,
                    "stt_response_format": self.stt_service.client.response_format,
                    "vad_noise_level": 0,
                    "vad_aggressiveness": self.stt_service.config.vad_aggressiveness,
                    "vad_min_speech_seconds": self.stt_service.config.vad_min_speech_seconds,
                    "tts_model": self.tts_service.client.model,
                    "tts_voice": self.tts_service.client.voice,
                    "tts_language": self.tts_service.client.language,
                    "tts_response_format": self.tts_service.client.response_format,
                    "tts_speed": str(self.tts_service.client.speed),
                }
            ]
        active_name = str(settings.get("active_profile", "")).strip() or self._profiles[0]["name"]
        self.settings_panel.apply_profiles(self._profiles, active_name)
        self._set_listening_profiles(self._profiles, active_name)

    def attach_tts_profiles(self, settings: dict, on_tts_profiles_changed=None):
        self._on_tts_profiles_changed = on_tts_profiles_changed
        profiles = settings.get("tts_profiles", [])
        self._tts_profiles = [
            dict(p)
            for p in profiles
            if isinstance(p, dict) and isinstance(p.get("name"), str) and p["name"].strip()
        ]
        if not self._tts_profiles:
            self._tts_profiles = [
                {
                    "name": "Default Voice",
                    "voice_filter_language": "any",
                    "voice_filter_gender": "any",
                    "tts_model": self.tts_service.client.model,
                    "tts_voice": self.tts_service.client.voice,
                    "tts_language": self.tts_service.client.language,
                    "tts_response_format": self.tts_service.client.response_format,
                    "tts_speed": str(self.tts_service.client.speed),
                }
            ]
        active_name = str(settings.get("active_tts_profile", "")).strip() or self._tts_profiles[0]["name"]
        self.settings_panel.apply_tts_profiles(self._tts_profiles, active_name)
        self.tts_panel.set_tts_profiles(self._tts_profiles, active_name)
        self._apply_tts_profile_by_name(active_name, persist=False, sync_settings_panel=True, status_message=False)

    def attach_ui_settings(self, settings: dict, on_ui_settings_changed=None):
        self._on_ui_settings_changed = on_ui_settings_changed
        self.dark_mode = bool(settings.get("dark_mode", False))
        self.settings_panel.apply_ui_settings(self.dark_mode)
        self._apply_theme()
        self._set_server_status(self._server_online)
        self._sync_retry_last_failed_button()
        self._refresh_capture_button_styles()
        raw = str(settings.get("ui_splitter_sizes", "560,340")).strip()
        try:
            parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if len(parts) >= 2 and all(p > 50 for p in parts[:2]):
                self.main_splitter.setSizes(parts[:2])
        except ValueError:
            pass
        self._load_output_history(settings.get("output_history"))

    # ── Listening tab ──────────────────────────────────────────────

    def _build_capture_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self._wrap_capture_section("Listening (Automatic VAD)", self._build_listening_tab()))
        layout.addWidget(self._wrap_capture_section("Recording (Manual)", self._build_recording_tab()))
        layout.addWidget(self._wrap_capture_section("File Transcription", self._build_file_tab()))
        layout.addStretch()
        return tab

    @staticmethod
    def _wrap_capture_section(title: str, content: QWidget) -> QGroupBox:
        section = QGroupBox(title)
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.addWidget(content)
        return section

    def _build_listening_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        profile_row = QHBoxLayout()
        profile_row.setSpacing(8)
        profile_row.addWidget(QLabel("Listening Profile:"))
        self.combo_listening_profiles = QComboBox()
        self.combo_listening_profiles.setEditable(False)
        min_profile_chars = 25
        min_profile_width = self.combo_listening_profiles.fontMetrics().horizontalAdvance("M" * min_profile_chars)
        self.combo_listening_profiles.setMinimumWidth(min_profile_width + 36)
        self.combo_listening_profiles.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_listening_profiles.setMinimumContentsLength(min_profile_chars)
        self.combo_listening_profiles.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.combo_listening_profiles.currentTextChanged.connect(self._on_listening_profile_selected)
        profile_row.addWidget(self.combo_listening_profiles, 1)

        self.btn_server_state = QToolButton()
        self.btn_server_state.setText("")
        self.btn_server_state.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_server_state.setIconSize(QSize(16, 16))
        self.btn_server_state.setFixedSize(30, 30)
        self.btn_server_state.setIcon(ui_icon(self, "listening_server_status"))
        self.btn_server_state.setToolTip("Server: Connected")
        profile_row.addWidget(self.btn_server_state)

        self.btn_retry_last_failed = QToolButton()
        self.btn_retry_last_failed.setText("")
        self.btn_retry_last_failed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_retry_last_failed.setIconSize(QSize(16, 16))
        self.btn_retry_last_failed.setFixedSize(30, 30)
        self.btn_retry_last_failed.setIcon(ui_icon(self, "listening_retry_last"))
        self.btn_retry_last_failed.setToolTip("Recreate Last Message")
        self.btn_retry_last_failed.clicked.connect(self._retry_last_failed_transcription)
        profile_row.addWidget(self.btn_retry_last_failed)
        layout.addLayout(profile_row)

        self.btn_listen_toggle = QPushButton("Start Listening")
        self.btn_listen_toggle.setCheckable(True)
        self.btn_listen_toggle.clicked.connect(self._toggle_listening)
        layout.addWidget(self.btn_listen_toggle)
        self._set_server_status(True)
        self._sync_retry_last_failed_button()
        return tab

    def _toggle_listening(self, checked):
        if checked:
            self._start_listening()
        else:
            self._stop_listening()

    def _start_listening(self):
        if self.stt_service.is_listening():
            self._sync_listening_ui(True)
            return
        self.stt_service.start_listening()
        self._sync_listening_ui(self.stt_service.is_listening())

    def _stop_listening(self):
        if not self.stt_service.is_listening():
            self._sync_listening_ui(False)
            return
        self.stt_service.stop_listening()
        self._sync_listening_ui(self.stt_service.is_listening())

    def _sync_listening_ui(self, listening: bool):
        self.btn_listen_toggle.blockSignals(True)
        self.btn_listen_toggle.setChecked(listening)
        self.btn_listen_toggle.blockSignals(False)
        self.btn_listen_toggle.setText("Stop Listening" if listening else "Start Listening")
        self._set_listening_button_style(listening)
        self._sync_quick_listen_button(listening)
        self.statusBar().showMessage("Listening (VAD)..." if listening else "Ready")
        if self.tray:
            self.tray.set_state("listening" if listening else "idle")
            self.tray.action_listen.setText("Stop Listening" if listening else "Start Listening")

    # ── Recording tab ──────────────────────────────────────────────

    def _build_recording_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        btn_row = QHBoxLayout()

        self.btn_rec_start = QPushButton("Start")
        self.btn_rec_pause = QPushButton("Pause")
        self.btn_rec_stop = QPushButton("Stop")
        self.btn_rec_pause.setEnabled(False)
        self.btn_rec_stop.setEnabled(False)

        self.btn_rec_start.clicked.connect(self._rec_start)
        self.btn_rec_pause.clicked.connect(self._rec_pause)
        self.btn_rec_stop.clicked.connect(self._rec_stop)

        btn_row.addWidget(self.btn_rec_start)
        btn_row.addWidget(self.btn_rec_pause)
        btn_row.addWidget(self.btn_rec_stop)
        layout.addLayout(btn_row)
        return tab

    def _rec_start(self):
        self.stt_service.start_recording()
        self.btn_rec_start.setEnabled(False)
        self.btn_rec_pause.setEnabled(True)
        self.btn_rec_stop.setEnabled(True)
        self.statusBar().showMessage("Recording...")
        if self.tray:
            self.tray.set_state("recording")

    def _rec_pause(self):
        if self.btn_rec_pause.text() == "Pause":
            self.stt_service.pause_recording()
            self.btn_rec_pause.setText("Resume")
            self.statusBar().showMessage("Recording paused")
        else:
            self.stt_service.resume_recording()
            self.btn_rec_pause.setText("Pause")
            self.statusBar().showMessage("Recording...")

    def _rec_stop(self):
        self.stt_service.stop_recording_and_transcribe()
        self.btn_rec_start.setEnabled(True)
        self.btn_rec_pause.setEnabled(False)
        self.btn_rec_stop.setEnabled(False)
        self.btn_rec_pause.setText("Pause")
        self.statusBar().showMessage("Transcribing...")
        if self.tray:
            self.tray.set_state("idle")

    def _toggle_quick_listening(self):
        if self.stt_service.is_listening():
            self._stop_listening()
        else:
            self._start_listening()

    def _sync_quick_listen_button(self, listening: bool):
        if not hasattr(self, "btn_quick_listen"):
            return
        if listening:
            self.btn_quick_listen.setText("Stop Listen")
            self.btn_quick_listen.setToolTip("Stop listening mode")
        else:
            self.btn_quick_listen.setText("Listen")
            self.btn_quick_listen.setToolTip("Start listening mode")

    # ── File tab ───────────────────────────────────────────────────

    def _build_file_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        file_row = QHBoxLayout()
        self.btn_select_file = QPushButton("Select File")
        self.file_label = QLabel("No file selected")
        self.btn_select_file.clicked.connect(self._select_file)
        file_row.addWidget(self.btn_select_file)
        file_row.addWidget(self.file_label, 1)
        layout.addLayout(file_row)

        self.btn_transcribe_file = QPushButton("Transcribe")
        self.btn_transcribe_file.setEnabled(False)
        self.btn_transcribe_file.clicked.connect(self._transcribe_file)
        layout.addWidget(self.btn_transcribe_file)

        self._selected_file = None
        return tab

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*)"
        )
        if path:
            self._selected_file = path
            self.file_label.setText(path.rsplit("/", 1)[-1] if "/" in path else path.rsplit("\\", 1)[-1])
            self.btn_transcribe_file.setEnabled(True)

    def _transcribe_file(self):
        if not self._selected_file:
            return
        self.statusBar().showMessage("Transcribing file...")
        self.stt_service.transcribe_file(self._selected_file)

    # ── Settings panel signal handlers ─────────────────────────────

    def _on_hotkeys_saved(self, listen_hotkey: str, record_hotkey: str):
        if self._on_hotkeys_changed:
            self._on_hotkeys_changed(listen_hotkey, record_hotkey)
        self.statusBar().showMessage("Hotkeys updated")

    def _on_stt_settings_from_panel(self, settings: dict):
        self.stt_service.update_settings(
            language=settings.get("stt_language"),
            response_format=settings.get("stt_response_format"),
            vad_aggressiveness=settings.get("vad_aggressiveness"),
            vad_min_speech_seconds=settings.get("vad_min_speech_seconds"),
        )
        self.auto_copy_transcription = bool(settings.get("auto_copy_transcription", True))
        self.clear_output_after_copy = bool(settings.get("clear_output_after_copy", False))
        self.stop_listening_after_copy = bool(settings.get("stop_listening_after_copy", False))
        self.keep_wrapping_parentheses = bool(settings.get("keep_wrapping_parentheses", False))
        if self._on_stt_settings_changed:
            self._on_stt_settings_changed(settings)
        self.statusBar().showMessage("STT settings updated")

    def _on_tts_settings_from_panel(self, settings: dict):
        settings_clean = {k: v for k, v in settings.items() if not str(k).startswith("_")}
        silent = bool(settings.get("_silent"))
        self.tts_service.update_settings(
            model=settings_clean.get("tts_model"),
            voice=settings_clean.get("tts_voice"),
            language=settings_clean.get("tts_language"),
            response_format=settings_clean.get("tts_response_format"),
            speed=self._coerce_tts_speed_value(settings_clean.get("tts_speed")),
        )
        self.tts_panel.set_api_speed(self._coerce_tts_speed_value(settings_clean.get("tts_speed")) or 1.0)
        settings_clean["tts_optimize_long_text"] = self.tts_panel.should_optimize_long_text()
        settings_clean["tts_optimize_threshold_chars"] = self.tts_panel.get_optimize_threshold_chars()
        if self._on_tts_settings_changed and not silent:
            self._on_tts_settings_changed(settings_clean)
        if not silent:
            self.statusBar().showMessage("TTS settings updated")

    def _on_tts_optimization_settings_changed(self, enabled: bool, threshold_chars: int):
        if self._on_tts_settings_changed:
            self._on_tts_settings_changed(
                {
                    "tts_optimize_long_text": bool(enabled),
                    "tts_optimize_threshold_chars": int(threshold_chars),
                }
            )

    def _on_ui_settings_from_panel(self, settings: dict):
        dark_mode = bool(settings.get("dark_mode", False))
        changed = dark_mode != self.dark_mode
        self.dark_mode = dark_mode
        if changed:
            self._apply_theme()
            self._set_server_status(self._server_online)
            self._sync_retry_last_failed_button()
            self._refresh_capture_button_styles()
            self.statusBar().showMessage("Theme updated")
        if self._on_ui_settings_changed:
            self._on_ui_settings_changed({"dark_mode": self.dark_mode})

    def _on_profiles_from_panel(self, profile_data: dict):
        profiles = profile_data.get("profiles", [])
        self._profiles = [
            dict(p)
            for p in profiles
            if isinstance(p, dict) and isinstance(p.get("name"), str) and p["name"].strip()
        ]
        if not self._profiles:
            return
        active_name = str(profile_data.get("active_profile", "")).strip() or self._profiles[0]["name"]
        self._set_listening_profiles(self._profiles, active_name)
        self._apply_profile_by_name(active_name, persist=False, sync_settings_panel=False, status_message=False)
        if self._on_profiles_changed:
            self._on_profiles_changed(
                {
                    "profiles": self._profiles,
                    "active_profile": active_name,
                }
            )
        self.statusBar().showMessage("Profiles updated")

    def _set_listening_profiles(self, profiles: list[dict], active_name: str):
        names = [str(p.get("name", "")).strip() for p in profiles if isinstance(p, dict) and str(p.get("name", "")).strip()]
        self._updating_listening_profiles = True
        self.combo_listening_profiles.clear()
        for name in names:
            self.combo_listening_profiles.addItem(name)
        idx = self.combo_listening_profiles.findText(active_name)
        self.combo_listening_profiles.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_listening_profiles.setEnabled(bool(names))
        self._updating_listening_profiles = False

    def _find_profile_by_name(self, name: str):
        target = (name or "").strip()
        if not target:
            return None
        for profile in self._profiles:
            if str(profile.get("name", "")).strip() == target:
                return profile
        return None

    def _apply_profile_by_name(self, profile_name: str, persist: bool, sync_settings_panel: bool, status_message: bool) -> bool:
        name = (profile_name or "").strip()
        if not name:
            return False
        profile = self._find_profile_by_name(name)
        if not profile:
            return False
        self.combo_listening_profiles.blockSignals(True)
        self.combo_listening_profiles.setCurrentText(name)
        self.combo_listening_profiles.blockSignals(False)
        if sync_settings_panel:
            self.settings_panel.set_active_profile(name)
            self.settings_panel.apply_profile(profile)
        else:
            speed = self._coerce_tts_speed_value(profile.get("tts_speed", self.tts_service.client.speed))
            self.stt_service.update_settings(
                language=profile.get("stt_language"),
                response_format=profile.get("stt_response_format"),
                vad_aggressiveness=profile.get("vad_aggressiveness"),
                vad_min_speech_seconds=profile.get("vad_min_speech_seconds"),
            )
            self.tts_service.update_settings(
                model=profile.get("tts_model"),
                voice=profile.get("tts_voice"),
                language=profile.get("tts_language"),
                response_format=profile.get("tts_response_format"),
                speed=speed,
            )
        if persist and self._on_profiles_changed:
            self._on_profiles_changed(
                {
                    "profiles": self._profiles,
                    "active_profile": name,
                }
            )
        if status_message:
            self.statusBar().showMessage(f"Listening profile applied: {name}")
        return True

    def _on_listening_profile_selected(self, profile_name: str):
        if self._updating_listening_profiles:
            return
        self._apply_profile_by_name(
            profile_name,
            persist=True,
            sync_settings_panel=True,
            status_message=True,
        )

    def _on_tts_profiles_from_panel(self, profile_data: dict):
        profiles = profile_data.get("tts_profiles", [])
        self._tts_profiles = [
            dict(p)
            for p in profiles
            if isinstance(p, dict) and isinstance(p.get("name"), str) and p["name"].strip()
        ]
        if not self._tts_profiles:
            return
        active_name = str(profile_data.get("active_tts_profile", "")).strip() or self._tts_profiles[0]["name"]
        self.tts_panel.set_tts_profiles(self._tts_profiles, active_name)
        self._apply_tts_profile_by_name(active_name, persist=False, sync_settings_panel=True, status_message=False)
        if self._on_tts_profiles_changed:
            self._on_tts_profiles_changed(
                {
                    "tts_profiles": self._tts_profiles,
                    "active_tts_profile": active_name,
                }
            )
        self.statusBar().showMessage("TTS profiles updated")

    def _find_tts_profile_by_name(self, name: str):
        for profile in self._tts_profiles:
            if str(profile.get("name", "")).strip() == name:
                return profile
        return None

    def _apply_tts_profile_by_name(
        self,
        profile_name: str,
        persist: bool,
        sync_settings_panel: bool,
        status_message: bool,
    ) -> bool:
        name = (profile_name or "").strip()
        if not name:
            return False
        profile = self._find_tts_profile_by_name(name)
        if not profile:
            return False
        speed = self._coerce_tts_speed_value(profile.get("tts_speed", self.tts_service.client.speed))
        self.tts_service.update_settings(
            model=profile.get("tts_model"),
            voice=profile.get("tts_voice"),
            language=profile.get("tts_language"),
            response_format=profile.get("tts_response_format"),
            speed=speed,
        )
        self.tts_panel.set_api_speed(speed if speed is not None else self.tts_service.client.speed)
        self.tts_panel.set_active_tts_profile(name)
        if sync_settings_panel:
            self.settings_panel.set_active_tts_profile(name)
            self.settings_panel.apply_tts_profile(profile, emit_tts=False)
        if persist and self._on_tts_profiles_changed:
            self._on_tts_profiles_changed(
                {
                    "tts_profiles": self._tts_profiles,
                    "active_tts_profile": name,
                }
            )
        if status_message:
            self.statusBar().showMessage(f"TTS profile applied: {name}")
        return True

    def _on_tts_profile_selected(self, profile_name: str):
        self._apply_tts_profile_by_name(
            profile_name,
            persist=True,
            sync_settings_panel=True,
            status_message=True,
        )

    # ── Service callbacks (run on main thread via signals) ─────────

    def _on_transcription_done(self, text):
        self._set_server_status(True)
        self._sync_retry_last_failed_button()
        display_text = self._format_transcription_text(text)
        self._append_output_text(display_text)
        self._remember_output_snapshot(self.text_output.toPlainText(), source_label="Transcription")
        if self.auto_copy_transcription:
            copy_to_clipboard(display_text)
            output_cleared, listening_stopped = self._apply_post_copy_actions()
            status = "Transcription complete — copied to clipboard"
            if output_cleared:
                status += ", output cleared"
            if listening_stopped:
                status += ", listening stopped"
            self.statusBar().showMessage(status)
        else:
            self.statusBar().showMessage("Transcription complete")

    def _on_transcription_error(self, err):
        logger.error("Transcription failed: %s", err)
        self._append_output_text(f"[ERROR] {err}")
        if self._is_server_failure_message(err):
            self._set_server_status(False, str(err))
        self._sync_retry_last_failed_button()
        if "saved to '" in str(err):
            self.statusBar().showMessage("Transcription failed — audio was backed up locally")
        else:
            self.statusBar().showMessage("Transcription failed")

    def _on_tts_done_play(self, audio_bytes: bytes):
        self.tts_panel.set_generate_enabled(True)
        self.tts_panel.set_save_enabled(bool(audio_bytes))
        if not audio_bytes:
            self.statusBar().showMessage("TTS returned empty audio")
            return
        audio_format = detect_audio_format(audio_bytes)
        if audio_format != "wav":
            self.tts_panel.set_playback_available(False)
            self.tts_panel.set_playing(False)
            self._tts_ui_timer.stop()
            self.statusBar().showMessage(
                f"TTS generated {audio_format.upper()} audio; in-app playback supports WAV only. "
                "Set TTS response format to wav for Generate & Play."
            )
            return
        try:
            self.tts_playback.load_wav_bytes(audio_bytes)
            self.tts_playback.set_speed(self.tts_panel.get_playback_speed())
            self.tts_playback.set_pitch_semitones(self.tts_panel.get_playback_pitch())
            duration = self.tts_playback.get_duration_seconds()
            self.tts_panel.set_playback_available(True)
            self.tts_panel.set_duration(duration)
            self.tts_playback.play()
            self.tts_panel.set_playing(True)
            self._tts_ui_timer.start()
            self.statusBar().showMessage("Speech generated and playing")
        except Exception as e:
            self.statusBar().showMessage(f"TTS generated (playback failed): {e}")

    def _on_tts_error(self, err: str):
        logger.error("TTS failed: %s", err)
        self.tts_panel.set_generate_enabled(True)
        self.statusBar().showMessage(f"TTS failed: {err}")

    def _on_dialogue_reply(self, text: str):
        self.dialogue_panel.set_busy(False)
        self.dialogue_panel.append_assistant(text)
        self.statusBar().showMessage("Dialogue response ready")

    def _on_dialogue_error(self, err: str):
        logger.error("Dialogue failed: %s", err)
        self.dialogue_panel.set_busy(False)
        self.dialogue_panel.append_error(err)
        self.statusBar().showMessage(f"Dialogue failed: {err}")

    # ── TTS actions ────────────────────────────────────────────────

    def _sync_tts_settings_from_panel(self) -> bool:
        """Ensure latest UI values are used for the next synth request."""
        try:
            settings = self.settings_panel.collect_tts_settings()
            api_speed = self.tts_panel.get_api_speed()
            settings["tts_speed"] = str(api_speed)
            self.settings_panel.set_tts_speed_value(api_speed, emit=False)
            self.tts_service.update_settings(
                model=settings.get("tts_model"),
                voice=settings.get("tts_voice"),
                language=settings.get("tts_language"),
                response_format=settings.get("tts_response_format"),
                speed=self._coerce_tts_speed_value(settings.get("tts_speed")),
            )
            return True
        except Exception as e:
            self.statusBar().showMessage(f"TTS settings error: {e}")
            return False

    def _on_tts_generate(self, text: str):
        if not self._sync_tts_settings_from_panel():
            return
        response_format = str(self.tts_service.client.response_format or "").strip().lower() or "unknown"
        optimize_long_text = self.tts_panel.should_optimize_long_text()
        threshold_chars = self.tts_panel.get_optimize_threshold_chars()
        self.tts_panel.set_generate_enabled(False)
        self._stop_tts_playback(update_status=False)
        if response_format == "wav":
            self.statusBar().showMessage("Generating speech...")
        else:
            self.statusBar().showMessage(
                f"Generating {response_format.upper()} audio (playback controls require WAV)."
            )
        self.tts_service.synthesize(
            text,
            optimize_long_text=optimize_long_text,
            long_text_threshold_chars=threshold_chars,
        )

    def _load_tts_from_output(self):
        text = self.text_output.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("No transcription output to load")
            return
        self.tts_panel.set_text(text)
        self.statusBar().showMessage("Loaded transcription output into TTS")

    def _save_last_tts_audio(self):
        audio = self.tts_service.get_last_audio()
        if not audio:
            self.statusBar().showMessage("No TTS audio to save")
            return
        fmt = detect_audio_format(audio)
        default_ext = fmt if fmt in {"wav", "flac", "mp3", "ogg"} else "wav"
        if default_ext == "wav":
            dialog_filter = "WAV Audio (*.wav);;All Files (*)"
        elif default_ext == "flac":
            dialog_filter = "FLAC Audio (*.flac);;All Files (*)"
        elif default_ext == "mp3":
            dialog_filter = "MP3 Audio (*.mp3);;All Files (*)"
        else:
            dialog_filter = "OGG Audio (*.ogg);;All Files (*)"
        default_name = f"tts_output.{default_ext}"
        if self._tts_last_audio_dir:
            default_path = str(Path(self._tts_last_audio_dir) / default_name)
        else:
            default_path = default_name
        path, _ = QFileDialog.getSaveFileName(
            self, "Save TTS Audio", default_path, dialog_filter
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(audio)
            self._tts_last_audio_dir = str(Path(path).parent)
            self.statusBar().showMessage("TTS audio saved")
        except OSError as e:
            self.statusBar().showMessage(f"Failed to save audio: {e}")

    def _open_saved_tts_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Saved TTS Audio",
            self._tts_last_audio_dir,
            "Audio Files (*.wav *.flac *.mp3 *.ogg);;WAV Audio (*.wav);;All Files (*)",
        )
        if not path:
            return

        try:
            with open(path, "rb") as f:
                audio_bytes = f.read()
        except OSError as e:
            self.statusBar().showMessage(f"Failed to open audio file: {e}")
            return

        self._tts_last_audio_dir = str(Path(path).parent)
        audio_format = detect_audio_format(audio_bytes)
        if audio_format != "wav":
            self.tts_panel.set_playback_available(False)
            self.tts_panel.set_playing(False)
            self._tts_ui_timer.stop()
            self.statusBar().showMessage(
                f"Loaded {audio_format.upper()} file. In-app playback supports WAV only."
            )
            return

        try:
            self._stop_tts_playback(update_status=False)
            self.tts_playback.load_wav_bytes(audio_bytes)
            self.tts_playback.set_speed(self.tts_panel.get_playback_speed())
            self.tts_playback.set_pitch_semitones(self.tts_panel.get_playback_pitch())
            duration = self.tts_playback.get_duration_seconds()
            self.tts_panel.set_playback_available(True)
            self.tts_panel.set_duration(duration)
            self.tts_playback.play()
            self.tts_panel.set_playing(True)
            self._tts_ui_timer.start()
            self.statusBar().showMessage(f"Loaded and playing: {Path(path).name}")
        except Exception as e:
            self.statusBar().showMessage(f"Failed to load audio: {e}")

    def _toggle_tts_playback(self):
        if not self.tts_playback.has_audio():
            return
        if self.tts_playback.is_playing():
            self.tts_playback.pause()
            self.tts_panel.set_playing(False)
            self._tts_ui_timer.stop()
            self.statusBar().showMessage("Playback paused")
        else:
            self.tts_playback.play()
            self.tts_panel.set_playing(True)
            self.statusBar().showMessage("Playback playing")
            self._tts_ui_timer.start()

    def _stop_tts_playback(self, update_status: bool = True):
        self._tts_ui_timer.stop()
        self.tts_playback.stop()
        self.tts_panel.set_playing(False)
        self.tts_panel.set_position(0.0)
        if update_status:
            self.statusBar().showMessage("Playback stopped")

    def _seek_tts_playback(self, seconds: float):
        if not self.tts_playback.has_audio():
            return
        self.tts_playback.seek_seconds(seconds)
        self.tts_panel.set_position(self.tts_playback.get_position_seconds())

    def _set_tts_playback_speed(self, speed: float):
        self.tts_playback.set_speed(speed)

    def _set_tts_playback_pitch(self, pitch: float):
        self.tts_playback.set_pitch_semitones(pitch)

    def _on_tts_api_speed_changed(self, speed: float):
        speed_value = self._coerce_tts_speed_value(speed)
        if speed_value is None:
            return
        self.tts_service.update_settings(speed=speed_value)
        self.settings_panel.set_tts_speed_value(speed_value, emit=False)

    def _coerce_tts_speed_value(self, value) -> float | None:
        if value is None:
            return None
        raw = str(value).strip().replace(",", ".")
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return float(self.tts_service.client.speed)

    def _refresh_tts_playback_ui(self):
        if not self.tts_playback.has_audio():
            self._tts_ui_timer.stop()
            return
        duration = self.tts_playback.get_duration_seconds()
        position = self.tts_playback.get_position_seconds()
        playing = self.tts_playback.is_playing()
        self.tts_panel.set_duration(duration)
        self.tts_panel.set_position(position)
        self.tts_panel.set_playing(playing)
        if not playing:
            self._tts_ui_timer.stop()

    # ── Dialogue actions ───────────────────────────────────────────

    def _on_dialogue_send(self, text: str):
        message = (text or "").strip()
        if not message:
            self.statusBar().showMessage("Dialogue message cannot be empty")
            return

        model = self.dialogue_panel.get_model()
        system_prompt = self.dialogue_panel.get_system_prompt()
        include_history = self.dialogue_panel.should_include_history()
        self.dialogue_service.update_settings(
            model=model,
            system_prompt=system_prompt,
            include_history=include_history,
        )
        self._persist_dialogue_settings(
            {
                "chat_model": model,
                "chat_system_prompt": system_prompt,
                "chat_include_history": include_history,
            }
        )
        self.dialogue_panel.append_user(message)
        self.dialogue_panel.set_busy(True)
        self.statusBar().showMessage("Generating dialogue response...")
        self.dialogue_service.send(message)

    def _on_dialogue_reset(self):
        model = self.dialogue_panel.get_model()
        system_prompt = self.dialogue_panel.get_system_prompt()
        include_history = self.dialogue_panel.should_include_history()
        self.dialogue_service.update_settings(
            model=model,
            system_prompt=system_prompt,
            include_history=include_history,
            reset_history=True,
        )
        self._persist_dialogue_settings(
            {
                "chat_model": model,
                "chat_system_prompt": system_prompt,
                "chat_include_history": include_history,
            }
        )
        self.dialogue_panel.clear_dialogue()
        self.statusBar().showMessage("Dialogue history cleared")

    def _load_dialogue_from_output(self):
        text = self.text_output.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("No transcription output to load")
            return
        self.dialogue_panel.set_input_text(text)
        self.statusBar().showMessage("Loaded transcription output into Dialogue")

    def _on_dialogue_model_changed(self, model: str):
        self.dialogue_service.update_settings(model=model)
        self._persist_dialogue_settings({"chat_model": str(model or "").strip()})

    def _on_dialogue_system_prompt_changed(self, prompt: str):
        prompt_value = str(prompt or "").strip()
        self.dialogue_service.update_settings(system_prompt=prompt_value, reset_history=True)
        self.dialogue_panel.clear_dialogue()
        self._persist_dialogue_settings({"chat_system_prompt": prompt_value})
        self.statusBar().showMessage("Dialogue system prompt updated")

    def _on_dialogue_history_mode_changed(self, enabled: bool):
        include_history = bool(enabled)
        self.dialogue_service.update_settings(include_history=include_history, reset_history=True)
        self.dialogue_panel.clear_dialogue()
        self._persist_dialogue_settings({"chat_include_history": include_history})
        if include_history:
            self.statusBar().showMessage("Dialogue now includes conversation history")
        else:
            self.statusBar().showMessage("Dialogue now sends each message independently")

    # ── Voice dialogue ──────────────────────────────────────────────

    def _on_voice_start(self):
        model = self.dialogue_panel.get_model()
        system_prompt = self.dialogue_panel.get_system_prompt()
        include_history = self.dialogue_panel.should_include_history()
        self.dialogue_service.update_settings(
            model=model,
            system_prompt=system_prompt,
            include_history=include_history,
        )
        self.dialogue_panel.set_voice_active(True)
        self.voice_dialogue.start()
        self.statusBar().showMessage("Voice dialogue started")

    def _on_voice_stop(self):
        self.voice_dialogue.stop()
        self.dialogue_panel.set_voice_active(False)
        self.dialogue_panel.set_voice_state("")
        self.statusBar().showMessage("Voice dialogue stopped")

    def _on_voice_auto_listen_changed(self, enabled: bool):
        self.voice_dialogue.auto_listen = enabled

    _VOICE_STATE_LABELS = {
        "IDLE": "",
        "LISTENING": "Listening...",
        "TRANSCRIBING": "Transcribing...",
        "THINKING": "Thinking...",
        "SPEAKING": "Speaking...",
        "CANCELLING": "Stopping...",
    }

    def _on_voice_state_changed(self, state_name: str):
        label = self._VOICE_STATE_LABELS.get(state_name, "")
        self.dialogue_panel.set_voice_state(label)
        if state_name == "IDLE":
            self.dialogue_panel.set_voice_active(False)

    def _on_voice_user_transcript(self, text: str):
        self.dialogue_panel.append_user(text)

    def _on_voice_assistant_text(self, text: str):
        self.dialogue_panel.append_assistant(text)

    def _on_voice_error(self, err: str):
        logger.error("Voice dialogue error: %s", err)
        self.dialogue_panel.append_error(err)
        self.statusBar().showMessage(f"Voice dialogue error: {err}")

    def _on_voice_turn_complete(self):
        self.statusBar().showMessage("Voice dialogue turn complete")

    def toggle_voice_dialogue_from_external(self):
        self.show_and_focus()
        self.tabs.setCurrentIndex(2)  # Dialogue tab
        if self.voice_dialogue.state == VoiceDialogueState.IDLE:
            self._on_voice_start()
        else:
            self._on_voice_stop()

    def _persist_dialogue_settings(self, payload: dict):
        if self._on_dialogue_settings_changed:
            self._on_dialogue_settings_changed(payload)

    # ── Shared output logic ────────────────────────────────────────

    def _load_output_history(self, history_items):
        entries = []
        if isinstance(history_items, list):
            for item in history_items:
                if not isinstance(item, dict):
                    continue
                text = str(item.get("text", "")).strip()
                if not text:
                    continue
                created_at = str(item.get("created_at", "")).strip()
                name = str(item.get("name", "")).strip() or self._build_output_history_name(
                    text,
                    created_at,
                    "Saved",
                )
                entries.append(
                    {
                        "name": name,
                        "text": text,
                        "created_at": created_at,
                    }
                )
                if len(entries) >= OUTPUT_HISTORY_LIMIT:
                    break
        self._output_history = entries
        self._refresh_output_history_controls()

    def _remember_output_snapshot(self, text: str, source_label: str):
        cleaned = (text or "").strip()
        if not cleaned:
            return
        now_iso = datetime.now().isoformat(timespec="seconds")
        name = self._build_output_history_name(cleaned, now_iso, source_label)
        deduped = [item for item in self._output_history if item.get("text") != cleaned]
        deduped.insert(
            0,
            {
                "name": name,
                "text": cleaned,
                "created_at": now_iso,
            },
        )
        self._output_history = deduped[:OUTPUT_HISTORY_LIMIT]
        self._refresh_output_history_controls()
        self._persist_output_history()

    def _refresh_output_history_controls(self):
        if not hasattr(self, "combo_output_history"):
            return
        self.combo_output_history.blockSignals(True)
        self.combo_output_history.clear()
        for item in self._output_history:
            self.combo_output_history.addItem(str(item.get("name", "")).strip())
        self.combo_output_history.blockSignals(False)
        has_history = bool(self._output_history)
        self.combo_output_history.setEnabled(has_history)
        self.btn_restore_output.setEnabled(has_history)
        self.combo_output_history.setToolTip("Last three transcription outputs")
        self.btn_restore_output.setToolTip("Restore selected output to editor")

    def _persist_output_history(self):
        if self._on_ui_settings_changed:
            self._on_ui_settings_changed(
                {
                    "output_history": [dict(item) for item in self._output_history],
                }
            )

    def _restore_selected_output(self):
        index = self.combo_output_history.currentIndex()
        if index < 0 or index >= len(self._output_history):
            self.statusBar().showMessage("No saved output selected")
            return
        selected = self._output_history[index]
        text = str(selected.get("text", "")).strip()
        if not text:
            self.statusBar().showMessage("Saved output is empty")
            return
        self.text_output.setPlainText(text)
        self.statusBar().showMessage(f"Restored output: {selected.get('name', 'Saved output')}")

    @staticmethod
    def _build_output_history_name(text: str, created_at: str, source_label: str) -> str:
        stamp = MainWindow._format_history_stamp(created_at)
        preview = " ".join(str(text).split())
        if len(preview) > OUTPUT_HISTORY_PREVIEW_CHARS:
            preview = f"{preview[:OUTPUT_HISTORY_PREVIEW_CHARS].rstrip()}..."
        return f"{source_label} {stamp} | {preview}"

    @staticmethod
    def _format_history_stamp(created_at: str) -> str:
        raw = str(created_at or "").strip()
        if not raw:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            return datetime.fromisoformat(raw).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            normalized = raw.replace("T", " ")
            return normalized[:16] if len(normalized) >= 16 else normalized

    def _copy_output(self):
        text = self.text_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self._remember_output_snapshot(text, source_label="Copied")
            output_cleared, listening_stopped = self._apply_post_copy_actions()
            status = "Copied to clipboard"
            if output_cleared:
                status += ", output cleared"
            if listening_stopped:
                status += ", listening stopped"
            self.statusBar().showMessage(status)

    def _apply_post_copy_actions(self) -> tuple[bool, bool]:
        output_cleared = False
        listening_stopped = False
        if self.clear_output_after_copy:
            self.text_output.clear()
            output_cleared = True
        if self.stop_listening_after_copy and self.stt_service.is_listening():
            self._stop_listening()
            listening_stopped = True
        return output_cleared, listening_stopped

    def _format_transcription_text(self, text: str) -> str:
        raw = (text or "").strip()
        if self.keep_wrapping_parentheses:
            return raw
        cleaned = self._strip_wrapping_parentheses(raw)
        return cleaned or raw

    @staticmethod
    def _strip_wrapping_parentheses(text: str) -> str:
        value = (text or "").strip()
        # Remove quote wrappers first so cases like '"(hello)"' normalize correctly.
        quote_pairs = [
            ('"', '"'),
            ("'", "'"),
            ("`", "`"),
            ("“", "”"),
            ("‘", "’"),
        ]
        changed = True
        while changed and value:
            changed = False
            for left, right in quote_pairs:
                if len(value) < 2 or not value.startswith(left) or not value.endswith(right):
                    continue
                inner = value[len(left):len(value) - len(right)].strip()
                if not inner:
                    continue
                value = inner
                changed = True
                break

        paren_pairs = [
            ("(", ")"),
            ("（", "）"),
        ]
        changed = True
        while changed and value:
            changed = False
            for left, right in paren_pairs:
                if not MainWindow._is_wrapped_by_pair(value, left, right):
                    continue
                inner = value[len(left):len(value) - len(right)].strip()
                if not inner:
                    continue
                value = inner
                changed = True
                break
        return value

    @staticmethod
    def _is_wrapped_by_pair(value: str, left: str, right: str) -> bool:
        if len(value) < 2 or not value.startswith(left) or not value.endswith(right):
            return False
        depth = 0
        for i, ch in enumerate(value):
            if ch == left:
                depth += 1
            elif ch == right:
                depth -= 1
                if depth < 0:
                    return False
                if depth == 0 and i != len(value) - 1:
                    return False
        return depth == 0

    def _clear_output(self):
        self.text_output.clear()
        self.statusBar().showMessage("Output cleared")

    def _focus_output_for_edit(self):
        self.text_output.setFocus()
        cursor = self.text_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_output.setTextCursor(cursor)
        self.statusBar().showMessage("Output ready for editing")

    def _append_output_text(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        current = self.text_output.toPlainText().strip()
        if current:
            self.text_output.setPlainText(f"{current}\n{text}")
        else:
            self.text_output.setPlainText(text)

    # ── Tray / Window ──────────────────────────────────────────────

    def show_and_focus(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def toggle_listening_from_external(self):
        self.show_and_focus()
        self.tabs.setCurrentIndex(0)  # Capture tab
        self.btn_listen_toggle.click()

    def toggle_recording_from_external(self):
        self.show_and_focus()
        self.tabs.setCurrentIndex(0)  # Capture tab
        if self.stt_service.is_recording:
            self._rec_stop()
        else:
            self._rec_start()

    def _minimize_to_tray(self):
        self.hide()
        self.statusBar().showMessage("Running in tray")
        if self.tray:
            self.tray.showMessage(
                "ZestVoice",
                "App minimized to tray. Use the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )

    def _on_splitter_moved(self, _pos, _index):
        if self._on_ui_settings_changed:
            sizes = self.main_splitter.sizes()
            self._on_ui_settings_changed({"ui_splitter_sizes": f"{sizes[0]},{sizes[1]}"})

    @staticmethod
    def _is_server_failure_message(err: str) -> bool:
        msg = str(err or "").lower()
        signals = (
            "http",
            "timeout",
            "timed out",
            "connection",
            "request failed",
            "status code",
            "server",
            "captured audio was saved",
            "source audio was saved",
        )
        return any(token in msg for token in signals)

    def _set_server_status(self, online: bool, detail: str = ""):
        self._server_online = bool(online)
        icon_key = "listening_server_status"
        if self._server_online:
            tooltip = "Server: Connected"
            bg = "#6a9a81" if not self.dark_mode else "#4f7a68"
            border = "#58826d" if not self.dark_mode else "#456a5a"
        else:
            icon_key = "listening_server_offline"
            tooltip = "Server Offline - Stop Speaking"
            bg = "#b87474" if not self.dark_mode else "#9a6262"
            border = "#9f6464" if not self.dark_mode else "#865656"
        if detail:
            tooltip = f"{tooltip}\n{detail}"
        self.btn_server_state.setIcon(ui_icon(self, icon_key))
        self.btn_server_state.setToolTip(tooltip)
        self.btn_server_state.setStyleSheet(
            f"""
            QToolButton {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px;
            }}
            """
        )

    def _sync_retry_last_failed_button(self):
        enabled = self.stt_service.has_last_failed_capture()
        self.btn_retry_last_failed.setEnabled(enabled)
        if enabled:
            bg = "#6a86a3" if not self.dark_mode else "#5e738b"
            hover = "#7893af" if not self.dark_mode else "#6b8199"
            border = "#5c7893" if not self.dark_mode else "#51657c"
        else:
            bg = "#b0bfcd" if not self.dark_mode else "#4a5868"
            hover = bg
            border = "#9fb0c0" if not self.dark_mode else "#425060"
        self.btn_retry_last_failed.setStyleSheet(
            f"""
            QToolButton {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background: {hover};
            }}
            """
        )

    def _retry_last_failed_transcription(self):
        if not self.stt_service.retry_last_failed():
            self.statusBar().showMessage("No failed transcription available to retry")
            self._sync_retry_last_failed_button()
            return
        self.statusBar().showMessage("Recreating last failed message...")

    def _set_listening_button_style(self, listening: bool):
        if listening:
            base = "#8f3b3b" if not self.dark_mode else "#7a3030"
            hover = "#a14848" if not self.dark_mode else "#8b3737"
            pressed = "#7a3030" if not self.dark_mode else "#682626"
        else:
            base = "#a97845" if not self.dark_mode else "#986e43"
            hover = "#b78451" if not self.dark_mode else "#a77c4f"
            pressed = "#93673b" if not self.dark_mode else "#845f39"
        self._apply_button_palette(
            self.btn_listen_toggle,
            base=base,
            hover=hover,
            pressed=pressed,
        )
        if hasattr(self, "btn_quick_listen"):
            self._apply_button_palette(
                self.btn_quick_listen,
                base=base,
                hover=hover,
                pressed=pressed,
            )

    def _set_recording_button_styles(self, recording: bool):
        if not hasattr(self, "btn_rec_start"):
            return
        if self.dark_mode:
            start_base, start_hover, start_pressed = "#5a7f70", "#6a8f7f", "#4e6f63"
            pause_base, pause_hover, pause_pressed = "#4f7264", "#5d8474", "#456558"
            stop_base, stop_hover, stop_pressed = "#a26666", "#b27575", "#8d5858"
            disabled_bg, disabled_fg = "#445160", "#bcc8d8"
        else:
            start_base, start_hover, start_pressed = "#5f8873", "#6e9782", "#527762"
            pause_base, pause_hover, pause_pressed = "#557b69", "#638975", "#4a6c5c"
            stop_base, stop_hover, stop_pressed = "#b06a6a", "#bf7878", "#9a5d5d"
            disabled_bg, disabled_fg = "#cfd8e2", "#6b7786"
        self._apply_button_palette(
            self.btn_rec_start,
            base=start_base,
            hover=start_hover,
            pressed=start_pressed,
            disabled_bg=disabled_bg,
            disabled_text=disabled_fg,
        )
        self._apply_button_palette(
            self.btn_rec_pause,
            base=pause_base,
            hover=pause_hover,
            pressed=pause_pressed,
            disabled_bg=disabled_bg,
            disabled_text=disabled_fg,
        )
        self._apply_button_palette(
            self.btn_rec_stop,
            base=stop_base,
            hover=stop_hover,
            pressed=stop_pressed,
            disabled_bg=disabled_bg,
            disabled_text=disabled_fg,
        )

    def _set_file_button_styles(self):
        if not hasattr(self, "btn_select_file"):
            return
        if self.dark_mode:
            select_base, select_hover, select_pressed = "#6f7f57", "#7d8e64", "#5f6d4a"
            trans_base, trans_hover, trans_pressed = "#5e7d67", "#6d8c76", "#506b59"
            disabled_bg, disabled_fg = "#445160", "#bcc8d8"
        else:
            select_base, select_hover, select_pressed = "#718a58", "#7f9965", "#60764a"
            trans_base, trans_hover, trans_pressed = "#5f8872", "#6f9781", "#517764"
            disabled_bg, disabled_fg = "#cfd8e2", "#6b7786"
        self._apply_button_palette(
            self.btn_select_file,
            base=select_base,
            hover=select_hover,
            pressed=select_pressed,
        )
        self._apply_button_palette(
            self.btn_transcribe_file,
            base=trans_base,
            hover=trans_hover,
            pressed=trans_pressed,
            disabled_bg=disabled_bg,
            disabled_text=disabled_fg,
        )

    def _refresh_capture_button_styles(self):
        self._set_listening_button_style(self.stt_service.is_listening())
        self._set_recording_button_styles(self.stt_service.is_recording)
        self._set_file_button_styles()

    @staticmethod
    def _apply_button_palette(
        button: QPushButton,
        *,
        base: str,
        hover: str,
        pressed: str,
        text: str = "#ffffff",
        disabled_bg: Optional[str] = None,
        disabled_text: str = "#ffffff",
    ):
        disabled_bg = disabled_bg or base
        button.setStyleSheet(
            f"""
            QPushButton {{
                background: {base};
                color: {text};
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:pressed {{ background: {pressed}; }}
            QPushButton:disabled {{
                background: {disabled_bg};
                color: {disabled_text};
            }}
            """
        )

    def _update_minimum_width_for_tabs(self):
        """Set window minimum width so all top tabs stay fully visible."""
        self.ensurePolished()
        tab_bar = self.tabs.tabBar()
        tab_count = tab_bar.count()
        if tab_count <= 0:
            return

        tab_total = sum(tab_bar.tabSizeHint(i).width() for i in range(tab_count))
        if tab_total <= 0:
            return

        # Matches QTabBar stylesheet margin-right on each tab.
        tab_spacing_total = 4 * max(0, tab_count - 1)

        central_margins = self.centralWidget().contentsMargins() if self.centralWidget() else None
        tab_margins = self.tabs.contentsMargins()
        bar_margins = tab_bar.contentsMargins()

        margins_total = (
            tab_margins.left() + tab_margins.right()
            + bar_margins.left() + bar_margins.right()
            + (central_margins.left() + central_margins.right() if central_margins else 0)
        )

        # Small buffer for frame/chrome and minor style variance.
        calculated_min_width = tab_total + tab_spacing_total + margins_total + 36
        self.setMinimumWidth(max(560, calculated_min_width))

    def _apply_theme(self):
        if self.dark_mode:
            stylesheet = """
            QMainWindow { background: #12161c; }
            QTabWidget::pane { border: 1px solid #303b49; background: #1a1f27; border-radius: 8px; }
            QTabBar::tab {
                background: #222a34;
                color: #cfd7e4;
                border: 1px solid #303b49;
                padding: 6px 12px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #2b3442; border-bottom-color: #2b3442; color: #eef3f8; }
            QScrollArea#settingsScrollArea { background: #1a1f27; border: none; }
            QScrollArea#settingsScrollArea > QWidget#qt_scrollarea_viewport { background: #1a1f27; }
            QWidget#settingsScrollContent { background: #1a1f27; }
            QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #3a4554;
                border-radius: 6px;
                padding: 4px;
                background: #131922;
                color: #dce5f2;
            }
            QPushButton { background: #5a6d84; color: #f2f6fb; border: none; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover { background: #667a92; }
            QPushButton:pressed { background: #4d6076; }
            QToolButton[role="tts-adjust"] {
                background: #3a4656;
                color: #9fb0c3;
                border: 1px solid #4a5a6d;
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 22px;
            }
            QToolButton[role="tts-adjust"]:enabled {
                background: #9a7a53;
                color: #f6efe6;
                border: 1px solid #ad8b64;
            }
            QToolButton[role="tts-adjust"]:enabled:hover { background: #a88964; }
            QToolButton[role="tts-adjust"]:enabled:pressed { background: #856947; }
            QLabel { color: #cfd7e4; }
            QCheckBox { color: #cfd7e4; }
            QStatusBar { background: #1a1f27; color: #cfd7e4; border-top: 1px solid #303b49; }
            """
        else:
            stylesheet = """
            QMainWindow { background: #f3f7fb; }
            QTabWidget::pane { border: 1px solid #c8d6e5; background: #ffffff; border-radius: 8px; }
            QTabBar::tab { background: #dfeaf4; border: 1px solid #b8cadb; padding: 6px 12px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
            QScrollArea#settingsScrollArea { background: #ffffff; border: none; }
            QScrollArea#settingsScrollArea > QWidget#qt_scrollarea_viewport { background: #ffffff; }
            QWidget#settingsScrollContent { background: #ffffff; }
            QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #b8cadb;
                border-radius: 6px;
                padding: 4px;
                background: #fbfdff;
            }
            QPushButton { background: #2f6d9a; color: #ffffff; border: none; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover { background: #3c7cab; }
            QPushButton:pressed { background: #285f86; }
            QToolButton[role="tts-adjust"] {
                background: #e7eef6;
                color: #1f3b53;
                border: 1px solid #b8cadb;
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 22px;
            }
            QToolButton[role="tts-adjust"]:enabled:hover { background: #d7e5f3; }
            QToolButton[role="tts-adjust"]:enabled:pressed { background: #c7daec; }
            QLabel { color: #1f3b53; }
            QCheckBox { color: #1f3b53; }
            """
        self.setStyleSheet(stylesheet)
        self._refresh_capture_button_styles()
        self._update_minimum_width_for_tabs()

    def closeEvent(self, event):
        self.voice_dialogue.stop()
        self._tts_ui_timer.stop()
        self.tts_playback.close()
        event.accept()
        app = QApplication.instance()
        if app:
            app.quit()
