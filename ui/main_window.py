"""Main application window — coordinates services and UI panels."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog, QApplication,
    QSystemTrayIcon, QSplitter, QStyle, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.app_config import AppConfig
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService
from core.text_output import copy_to_clipboard
from core.audio_playback import play_wav_bytes
from ui.tts_panel import TTSPanel
from ui.settings_panel import SettingsPanel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with Listening / Recording / File tabs."""

    # Signals for thread-safe service callbacks
    _transcription_ready = pyqtSignal(str)
    _transcription_error = pyqtSignal(str)
    _tts_audio_ready = pyqtSignal(bytes)
    _tts_error = pyqtSignal(str)

    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__()
        self.setWindowTitle("LemonFox Transcriber")
        self.setMinimumSize(500, 400)

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

        # Connect signals to UI handlers (runs on main thread)
        self._transcription_ready.connect(self._on_transcription_done)
        self._transcription_error.connect(self._on_transcription_error)
        self._tts_audio_ready.connect(self._on_tts_done_play)
        self._tts_error.connect(self._on_tts_error)

        self.tray = None
        self._on_hotkeys_changed = None
        self._on_stt_settings_changed = None
        self._on_tts_settings_changed = None
        self._on_profiles_changed = None
        self._on_ui_settings_changed = None
        self.auto_copy_transcription = True

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
        self.tabs.addTab(self._build_listening_tab(), "Listening")
        self.tabs.setTabIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.tabs.addTab(self._build_recording_tab(), "Recording")
        self.tabs.setTabIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.tabs.addTab(self._build_file_tab(), "File")
        self.tabs.setTabIcon(2, self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

        # TTS panel (extracted widget)
        self.tts_panel = TTSPanel()
        self.tts_panel.generate_requested.connect(self._on_tts_generate)
        self.tts_panel.use_output_requested.connect(self._load_tts_from_output)
        self.tts_panel.save_audio_requested.connect(self._save_last_tts_audio)
        self.tabs.addTab(self.tts_panel, "Text to Speech")
        self.tabs.setTabIcon(3, self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))

        # Settings panel (extracted widget)
        self.settings_panel = SettingsPanel()
        self.settings_panel.hotkeys_save_requested.connect(self._on_hotkeys_saved)
        self.settings_panel.stt_settings_changed.connect(self._on_stt_settings_from_panel)
        self.settings_panel.tts_settings_changed.connect(self._on_tts_settings_from_panel)
        self.settings_panel.profiles_changed.connect(self._on_profiles_from_panel)
        self.tabs.addTab(self.settings_panel, "Settings")
        self.tabs.setTabIcon(4, self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))

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

        btn_row = QHBoxLayout()
        self.btn_minimize_tray = QPushButton("Minimize to Tray")
        self.btn_minimize_tray.clicked.connect(self._minimize_to_tray)
        self.btn_minimize_tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self.btn_edit_output = QPushButton("Edit Output")
        self.btn_edit_output.clicked.connect(self._focus_output_for_edit)
        self.btn_edit_output.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self._clear_output)
        self.btn_clear.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy_output)
        self.btn_copy.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        btn_row.addStretch()
        btn_row.addWidget(self.btn_minimize_tray)
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
        listen_hotkey, record_hotkey = hotkeys.get_hotkeys()
        self.settings_panel.attach_hotkey_manager(hotkeys, listen_hotkey, record_hotkey)

    def attach_stt_settings(self, settings: dict, on_stt_settings_changed=None):
        self._on_stt_settings_changed = on_stt_settings_changed
        self.settings_panel.apply_stt_settings(
            language=settings.get("stt_language", self.stt_service.client.language),
            response_format=settings.get("stt_response_format", self.stt_service.client.response_format),
            auto_copy=bool(settings.get("auto_copy_transcription", True)),
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

    def attach_profiles(self, settings: dict, on_profiles_changed=None):
        self._on_profiles_changed = on_profiles_changed
        profiles = settings.get("profiles", [])
        active_name = settings.get("active_profile", "Default")
        self.settings_panel.apply_profiles(profiles, active_name)

    def attach_ui_settings(self, settings: dict, on_ui_settings_changed=None):
        self._on_ui_settings_changed = on_ui_settings_changed
        raw = str(settings.get("ui_splitter_sizes", "560,340")).strip()
        try:
            parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if len(parts) >= 2 and all(p > 50 for p in parts[:2]):
                self.main_splitter.setSizes(parts[:2])
        except ValueError:
            pass

    # ── Listening tab ──────────────────────────────────────────────

    def _build_listening_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.btn_listen_toggle = QPushButton("Start Listening")
        self.btn_listen_toggle.setCheckable(True)
        self.btn_listen_toggle.clicked.connect(self._toggle_listening)
        layout.addWidget(self.btn_listen_toggle)
        layout.addStretch()
        return tab

    def _toggle_listening(self, checked):
        if checked:
            self._start_listening()
        else:
            self._stop_listening()

    def _start_listening(self):
        if self.stt_service.is_listening():
            return
        self._sync_listening_ui(True)
        self.stt_service.start_listening()

    def _stop_listening(self):
        self.stt_service.stop_listening()
        self._sync_listening_ui(False)

    def _sync_listening_ui(self, listening: bool):
        self.btn_listen_toggle.blockSignals(True)
        self.btn_listen_toggle.setChecked(listening)
        self.btn_listen_toggle.blockSignals(False)
        self.btn_listen_toggle.setText("Stop Listening" if listening else "Start Listening")
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
        layout.addStretch()
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
        layout.addStretch()

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
        )
        self.auto_copy_transcription = bool(settings.get("auto_copy_transcription", True))
        if self._on_stt_settings_changed:
            self._on_stt_settings_changed(settings)
        self.statusBar().showMessage("STT settings updated")

    def _on_tts_settings_from_panel(self, settings: dict):
        self.tts_service.update_settings(
            model=settings.get("tts_model"),
            voice=settings.get("tts_voice"),
            language=settings.get("tts_language"),
            response_format=settings.get("tts_response_format"),
            speed=float(settings["tts_speed"]) if settings.get("tts_speed") else None,
        )
        if self._on_tts_settings_changed:
            self._on_tts_settings_changed(settings)
        self.statusBar().showMessage("TTS settings updated")

    def _on_profiles_from_panel(self, profile_data: dict):
        if self._on_profiles_changed:
            self._on_profiles_changed(profile_data)

    # ── Service callbacks (run on main thread via signals) ─────────

    def _on_transcription_done(self, text):
        self._append_output_text(text)
        if self.auto_copy_transcription:
            copy_to_clipboard(text)
            self.statusBar().showMessage("Transcription complete — copied to clipboard")
        else:
            self.statusBar().showMessage("Transcription complete")

    def _on_transcription_error(self, err):
        logger.error("Transcription failed: %s", err)
        self.text_output.setPlainText(f"Error: {err}")
        self.statusBar().showMessage("Transcription failed")

    def _on_tts_done_play(self, audio_bytes: bytes):
        self.tts_panel.set_generate_enabled(True)
        self.tts_panel.set_save_enabled(bool(audio_bytes))
        if not audio_bytes:
            self.statusBar().showMessage("TTS returned empty audio")
            return
        try:
            play_wav_bytes(audio_bytes)
            self.statusBar().showMessage("Speech generated and playing")
        except Exception as e:
            self.statusBar().showMessage(f"TTS generated (playback failed): {e}")

    def _on_tts_error(self, err: str):
        logger.error("TTS failed: %s", err)
        self.tts_panel.set_generate_enabled(True)
        self.statusBar().showMessage(f"TTS failed: {err}")

    # ── TTS actions ────────────────────────────────────────────────

    def _on_tts_generate(self, text: str):
        self.tts_panel.set_generate_enabled(False)
        self.statusBar().showMessage("Generating speech...")
        self.tts_service.synthesize(text)

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
        path, _ = QFileDialog.getSaveFileName(
            self, "Save TTS Audio", "tts_output.wav", "WAV Audio (*.wav);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(audio)
            self.statusBar().showMessage("TTS audio saved")
        except OSError as e:
            self.statusBar().showMessage(f"Failed to save audio: {e}")

    # ── Shared output logic ────────────────────────────────────────

    def _copy_output(self):
        text = self.text_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("Copied to clipboard")

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

    def _minimize_to_tray(self):
        self.hide()
        self.statusBar().showMessage("Running in tray")
        if self.tray:
            self.tray.showMessage(
                "LimeScribe",
                "App minimized to tray. Use the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )

    def _on_splitter_moved(self, _pos, _index):
        if self._on_ui_settings_changed:
            sizes = self.main_splitter.sizes()
            self._on_ui_settings_changed({"ui_splitter_sizes": f"{sizes[0]},{sizes[1]}"})

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #f3f7fb; }
            QTabWidget::pane { border: 1px solid #c8d6e5; background: #ffffff; border-radius: 8px; }
            QTabBar::tab { background: #dfeaf4; border: 1px solid #b8cadb; padding: 6px 12px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
            QTextEdit, QLineEdit, QComboBox { border: 1px solid #b8cadb; border-radius: 6px; padding: 4px; background: #fbfdff; }
            QPushButton { background: #2f6d9a; color: #ffffff; border: none; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover { background: #3c7cab; }
            QPushButton:pressed { background: #285f86; }
            QLabel { color: #1f3b53; }
            """
        )

    def closeEvent(self, event):
        event.accept()
        app = QApplication.instance()
        if app:
            app.quit()
