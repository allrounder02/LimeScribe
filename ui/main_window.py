from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog, QLineEdit, QMessageBox, QApplication, QComboBox,
    QSystemTrayIcon,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logging

from core.lemonfox_client import LemonFoxClient
from core.lemonfox_tts_client import LemonFoxTTSClient
from core.audio_recorder import AudioRecorder
from core.vad_listener import VADListener
from core.text_output import copy_to_clipboard
from core.tts_audio_output import play_wav_bytes
from hotkeys import DEFAULT_HOTKEY_LISTEN, DEFAULT_HOTKEY_RECORD
from config import (
    LEMONFOX_TTS_MODEL,
    LEMONFOX_TTS_VOICE,
    LEMONFOX_TTS_LANGUAGE,
    LEMONFOX_TTS_RESPONSE_FORMAT,
    LEMONFOX_TTS_SPEED,
)

logger = logging.getLogger(__name__)

TTS_MODEL_PRESETS = ["tts-1", "tts-1-hd"]
TTS_VOICE_PRESETS = ["heart", "alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse"]
TTS_LANGUAGE_PRESETS = ["en-us", "en-gb", "de-de", "fr-fr", "es-es", "it-it"]
TTS_RESPONSE_FORMAT_PRESETS = ["wav", "mp3", "ogg", "flac"]


class TranscribeWorker(QThread):
    """Background thread for API calls so the GUI stays responsive."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client: LemonFoxClient, audio_bytes: bytes = None, file_path: str = None):
        super().__init__()
        self.client = client
        self.audio_bytes = audio_bytes
        self.file_path = file_path

    def run(self):
        try:
            if self.file_path:
                text = self.client.transcribe_file(self.file_path)
            elif self.audio_bytes:
                text = self.client.transcribe_bytes(self.audio_bytes)
            else:
                self.error.emit("No audio provided.")
                return
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class TTSSynthesizeWorker(QThread):
    """Background thread for TTS API calls."""

    finished = pyqtSignal(bytes)
    error = pyqtSignal(str)

    def __init__(self, client: LemonFoxTTSClient, text: str):
        super().__init__()
        self.client = client
        self.text = text

    def run(self):
        try:
            audio_bytes = self.client.synthesize(self.text)
            self.finished.emit(audio_bytes)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window with Listening / Recording / File tabs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LemonFox Transcriber")
        self.setMinimumSize(500, 400)

        self.client = LemonFoxClient()
        self.tts_client = LemonFoxTTSClient()
        self.recorder = AudioRecorder()
        self.tray = None  # Set by app.py after construction
        self._worker = None
        self._tts_worker = None
        self._tts_last_audio = b""
        self._vad = None
        self._listen_workers = []  # keep refs so they don't get GC'd
        self.hotkeys = None
        self._on_hotkeys_changed = None
        self._on_tts_settings_changed = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_listening_tab(), "Listening")
        self.tabs.addTab(self._build_recording_tab(), "Recording")
        self.tabs.addTab(self._build_file_tab(), "File")
        self.tabs.addTab(self._build_tts_tab(), "Text to Speech")
        self.tabs.addTab(self._build_settings_tab(), "Settings")
        layout.addWidget(self.tabs)

        # Shared output area
        self.output_label = QLabel("Transcription Output:")
        layout.addWidget(self.output_label)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(False)
        self.text_output.setPlaceholderText("Transcription output appears here. You can edit it directly.")
        layout.addWidget(self.text_output)

        # Output actions
        btn_row = QHBoxLayout()
        self.btn_minimize_tray = QPushButton("Minimize to Tray")
        self.btn_minimize_tray.clicked.connect(self._minimize_to_tray)
        self.btn_edit_output = QPushButton("Edit Output")
        self.btn_edit_output.clicked.connect(self._focus_output_for_edit)
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self._clear_output)
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy_output)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_minimize_tray)
        btn_row.addWidget(self.btn_edit_output)
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_copy)
        layout.addLayout(btn_row)

        # Status bar
        self.statusBar().showMessage("Ready")

    def attach_tray(self, tray):
        """Attach tray and sync UI/menu labels to current state."""
        self.tray = tray
        self._sync_listening_ui(self.btn_listen_toggle.isChecked())

    def attach_hotkey_manager(self, hotkeys, on_hotkeys_changed=None):
        """Attach global hotkey manager so settings tab can edit bindings."""
        self.hotkeys = hotkeys
        self._on_hotkeys_changed = on_hotkeys_changed
        listen_hotkey, record_hotkey = self.hotkeys.get_hotkeys()
        self.input_listen_hotkey.setText(listen_hotkey)
        self.input_record_hotkey.setText(record_hotkey)

    def attach_tts_settings(self, settings: dict, on_tts_settings_changed=None):
        """Attach persisted TTS settings and apply to client/live UI."""
        self._on_tts_settings_changed = on_tts_settings_changed
        self._set_combo_value(self.input_tts_model, settings.get("tts_model", self.tts_client.model))
        self._set_combo_value(self.input_tts_voice, settings.get("tts_voice", self.tts_client.voice))
        self._set_combo_value(self.input_tts_language, settings.get("tts_language", self.tts_client.language))
        self._set_combo_value(
            self.input_tts_response_format,
            settings.get("tts_response_format", self.tts_client.response_format),
        )
        self.input_tts_speed.setText(str(settings.get("tts_speed", self.tts_client.speed)))
        self._save_tts_settings_ui(show_status=False)

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
        if self._vad:
            return
        self._sync_listening_ui(True)
        self._vad = VADListener(on_speech_chunk=self._on_vad_chunk)
        self._vad.start()

    def _stop_listening(self):
        if not self._vad:
            self._sync_listening_ui(False)
            return
        if self._vad:
            self._vad.stop()
            self._vad = None
        self._sync_listening_ui(False)

    def _sync_listening_ui(self, listening: bool):
        """Keep button text/check state and tray menu/icon in sync."""
        self.btn_listen_toggle.blockSignals(True)
        self.btn_listen_toggle.setChecked(listening)
        self.btn_listen_toggle.blockSignals(False)
        self.btn_listen_toggle.setText("Stop Listening" if listening else "Start Listening")
        self.statusBar().showMessage("Listening (VAD)..." if listening else "Ready")
        if self.tray:
            self.tray.set_state("listening" if listening else "idle")
            self.tray.action_listen.setText("Stop Listening" if listening else "Start Listening")

    def _on_vad_chunk(self, wav_bytes: bytes):
        """Called from VAD background thread when a speech chunk is ready."""
        worker = TranscribeWorker(self.client, audio_bytes=wav_bytes)
        worker.finished.connect(self._on_listen_transcription)
        worker.error.connect(self._on_transcription_error)
        worker.finished.connect(lambda: self._listen_workers.remove(worker))
        worker.error.connect(lambda: self._listen_workers.remove(worker))
        self._listen_workers.append(worker)
        worker.start()

    def _on_listen_transcription(self, text):
        """Append transcribed text in listening mode (continuous) and copy to clipboard."""
        self._append_output_text(text)
        copy_to_clipboard(text)
        self.statusBar().showMessage("Listening (VAD)...")

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
        self.recorder.start()
        self.btn_rec_start.setEnabled(False)
        self.btn_rec_pause.setEnabled(True)
        self.btn_rec_stop.setEnabled(True)
        self.statusBar().showMessage("Recording...")
        if self.tray:
            self.tray.set_state("recording")

    def _rec_pause(self):
        if self.btn_rec_pause.text() == "Pause":
            self.recorder.pause()
            self.btn_rec_pause.setText("Resume")
            self.statusBar().showMessage("Recording paused")
        else:
            self.recorder.resume()
            self.btn_rec_pause.setText("Pause")
            self.statusBar().showMessage("Recording...")

    def _rec_stop(self):
        wav_bytes = self.recorder.stop()
        self.btn_rec_start.setEnabled(True)
        self.btn_rec_pause.setEnabled(False)
        self.btn_rec_stop.setEnabled(False)
        self.btn_rec_pause.setText("Pause")
        if self.tray:
            self.tray.set_state("idle")
        if not wav_bytes:
            self.statusBar().showMessage("No audio captured")
            return
        self.statusBar().showMessage("Transcribing...")
        self._run_transcription(audio_bytes=wav_bytes)

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
        self._run_transcription(file_path=self._selected_file)

    # ── Text-to-Speech tab ────────────────────────────────────────
    def _build_tts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.tts_input = QTextEdit()
        self.tts_input.setPlaceholderText("Enter text to synthesize, or load from transcription output.")
        layout.addWidget(self.tts_input)

        btn_row = QHBoxLayout()
        self.btn_tts_from_output = QPushButton("Use Transcription Output")
        self.btn_tts_generate_play = QPushButton("Generate & Play")
        self.btn_tts_save_audio = QPushButton("Save Last Audio")
        self.btn_tts_save_audio.setEnabled(False)

        self.btn_tts_from_output.clicked.connect(self._load_tts_from_output)
        self.btn_tts_generate_play.clicked.connect(self._generate_tts_and_play)
        self.btn_tts_save_audio.clicked.connect(self._save_last_tts_audio)

        btn_row.addWidget(self.btn_tts_from_output)
        btn_row.addWidget(self.btn_tts_generate_play)
        btn_row.addWidget(self.btn_tts_save_audio)
        layout.addLayout(btn_row)
        layout.addStretch()
        return tab

    # ── Settings tab ───────────────────────────────────────────────
    def _build_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Global Hotkeys"))
        layout.addWidget(QLabel("Format example: Ctrl+Alt+L"))

        listen_row = QHBoxLayout()
        listen_row.addWidget(QLabel("Toggle Listening:"))
        self.input_listen_hotkey = QLineEdit(DEFAULT_HOTKEY_LISTEN)
        listen_row.addWidget(self.input_listen_hotkey)
        layout.addLayout(listen_row)

        record_row = QHBoxLayout()
        record_row.addWidget(QLabel("Toggle Recording:"))
        self.input_record_hotkey = QLineEdit(DEFAULT_HOTKEY_RECORD)
        record_row.addWidget(self.input_record_hotkey)
        layout.addLayout(record_row)

        btn_row = QHBoxLayout()
        self.btn_hotkeys_save = QPushButton("Save Hotkeys")
        self.btn_hotkeys_defaults = QPushButton("Restore Defaults")
        self.btn_hotkeys_save.clicked.connect(self._save_hotkeys)
        self.btn_hotkeys_defaults.clicked.connect(self._restore_default_hotkeys)
        btn_row.addWidget(self.btn_hotkeys_save)
        btn_row.addWidget(self.btn_hotkeys_defaults)
        layout.addLayout(btn_row)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Text-to-Speech"))
        layout.addWidget(QLabel("Supported fields: model, voice, language, response format, speed"))

        tts_model_row = QHBoxLayout()
        tts_model_row.addWidget(QLabel("Model:"))
        self.input_tts_model = QComboBox()
        self.input_tts_model.setEditable(True)
        self.input_tts_model.addItems(TTS_MODEL_PRESETS)
        self.input_tts_model.setCurrentText(LEMONFOX_TTS_MODEL)
        tts_model_row.addWidget(self.input_tts_model)
        layout.addLayout(tts_model_row)

        tts_voice_row = QHBoxLayout()
        tts_voice_row.addWidget(QLabel("Voice:"))
        self.input_tts_voice = QComboBox()
        self.input_tts_voice.setEditable(True)
        self.input_tts_voice.addItems(TTS_VOICE_PRESETS)
        self.input_tts_voice.setCurrentText(LEMONFOX_TTS_VOICE)
        tts_voice_row.addWidget(self.input_tts_voice)
        layout.addLayout(tts_voice_row)

        tts_lang_row = QHBoxLayout()
        tts_lang_row.addWidget(QLabel("Language:"))
        self.input_tts_language = QComboBox()
        self.input_tts_language.setEditable(True)
        self.input_tts_language.addItems(TTS_LANGUAGE_PRESETS)
        self.input_tts_language.setCurrentText(LEMONFOX_TTS_LANGUAGE)
        tts_lang_row.addWidget(self.input_tts_language)
        layout.addLayout(tts_lang_row)

        tts_fmt_row = QHBoxLayout()
        tts_fmt_row.addWidget(QLabel("Response Format:"))
        self.input_tts_response_format = QComboBox()
        self.input_tts_response_format.setEditable(True)
        self.input_tts_response_format.addItems(TTS_RESPONSE_FORMAT_PRESETS)
        self.input_tts_response_format.setCurrentText(LEMONFOX_TTS_RESPONSE_FORMAT)
        tts_fmt_row.addWidget(self.input_tts_response_format)
        layout.addLayout(tts_fmt_row)

        tts_speed_row = QHBoxLayout()
        tts_speed_row.addWidget(QLabel("Speed:"))
        self.input_tts_speed = QLineEdit(str(LEMONFOX_TTS_SPEED))
        tts_speed_row.addWidget(self.input_tts_speed)
        layout.addLayout(tts_speed_row)

        tts_btn_row = QHBoxLayout()
        self.btn_tts_settings_save = QPushButton("Save TTS Settings")
        self.btn_tts_settings_defaults = QPushButton("Restore TTS Defaults")
        self.btn_tts_settings_save.clicked.connect(self._save_tts_settings_ui)
        self.btn_tts_settings_defaults.clicked.connect(self._restore_default_tts_settings)
        tts_btn_row.addWidget(self.btn_tts_settings_save)
        tts_btn_row.addWidget(self.btn_tts_settings_defaults)
        layout.addLayout(tts_btn_row)

        layout.addStretch()
        return tab

    def _save_hotkeys(self):
        if not self.hotkeys:
            self.statusBar().showMessage("Hotkey manager is not ready")
            return

        listen_hotkey = self.input_listen_hotkey.text().strip()
        record_hotkey = self.input_record_hotkey.text().strip()
        try:
            self.hotkeys.update_hotkeys(listen_hotkey, record_hotkey)
            applied_listen, applied_record = self.hotkeys.get_hotkeys()
            self.input_listen_hotkey.setText(applied_listen)
            self.input_record_hotkey.setText(applied_record)
            if self._on_hotkeys_changed:
                self._on_hotkeys_changed(applied_listen, applied_record)
            self.statusBar().showMessage("Hotkeys updated")
        except Exception as e:
            QMessageBox.warning(self, "Hotkey Error", str(e))
            self.statusBar().showMessage("Hotkey update failed")

    def _restore_default_hotkeys(self):
        self.input_listen_hotkey.setText(DEFAULT_HOTKEY_LISTEN)
        self.input_record_hotkey.setText(DEFAULT_HOTKEY_RECORD)
        self._save_hotkeys()

    def _collect_tts_settings_from_ui(self) -> dict:
        model = self.input_tts_model.currentText().strip()
        voice = self.input_tts_voice.currentText().strip()
        language = self.input_tts_language.currentText().strip()
        response_format = self.input_tts_response_format.currentText().strip().lower()
        speed_raw = self.input_tts_speed.text().strip()

        if not model or not voice or not language or not response_format:
            raise ValueError("Model, voice, language, and response format are required.")
        speed = float(speed_raw)
        if speed <= 0:
            raise ValueError("Speed must be greater than 0.")

        return {
            "tts_model": model,
            "tts_voice": voice,
            "tts_language": language,
            "tts_response_format": response_format,
            "tts_speed": str(speed),
        }

    def _apply_tts_settings_to_client(self, settings: dict):
        self.tts_client.model = settings["tts_model"]
        self.tts_client.voice = settings["tts_voice"]
        self.tts_client.language = settings["tts_language"]
        self.tts_client.response_format = settings["tts_response_format"]
        self.tts_client.speed = float(settings["tts_speed"])

    def _save_tts_settings_ui(self, show_status=True):
        try:
            settings = self._collect_tts_settings_from_ui()
            self._apply_tts_settings_to_client(settings)
            if self._on_tts_settings_changed:
                self._on_tts_settings_changed(settings)
            if show_status:
                self.statusBar().showMessage("TTS settings updated")
        except Exception as e:
            if show_status:
                QMessageBox.warning(self, "TTS Settings Error", str(e))
            if show_status:
                self.statusBar().showMessage("TTS settings update failed")

    def _restore_default_tts_settings(self):
        self._set_combo_value(self.input_tts_model, LEMONFOX_TTS_MODEL)
        self._set_combo_value(self.input_tts_voice, LEMONFOX_TTS_VOICE)
        self._set_combo_value(self.input_tts_language, LEMONFOX_TTS_LANGUAGE)
        self._set_combo_value(self.input_tts_response_format, LEMONFOX_TTS_RESPONSE_FORMAT)
        self.input_tts_speed.setText(str(LEMONFOX_TTS_SPEED))
        self._save_tts_settings_ui()

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str):
        if value is None:
            value = ""
        combo.setCurrentText(str(value))

    # ── Shared transcription logic ─────────────────────────────────
    def _run_transcription(self, audio_bytes=None, file_path=None):
        self._worker = TranscribeWorker(self.client, audio_bytes=audio_bytes, file_path=file_path)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_transcription_error)
        self._worker.start()

    def _on_transcription_done(self, text):
        self._append_output_text(text)
        copy_to_clipboard(text)
        self.statusBar().showMessage("Transcription complete — copied to clipboard")

    def _on_transcription_error(self, err):
        logger.error("Transcription failed: %s", err)
        self.text_output.setPlainText(f"Error: {err}")
        self.statusBar().showMessage("Transcription failed")

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

    def _load_tts_from_output(self):
        text = self.text_output.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("No transcription output to load")
            return
        self.tts_input.setPlainText(text)
        self.statusBar().showMessage("Loaded transcription output into TTS")

    def _generate_tts_and_play(self):
        text = self.tts_input.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("No TTS input text")
            return

        self.btn_tts_generate_play.setEnabled(False)
        self.statusBar().showMessage("Generating speech...")

        self._tts_worker = TTSSynthesizeWorker(self.tts_client, text)
        self._tts_worker.finished.connect(self._on_tts_done_play)
        self._tts_worker.error.connect(self._on_tts_error)
        self._tts_worker.start()

    def _on_tts_done_play(self, audio_bytes: bytes):
        self._tts_last_audio = audio_bytes or b""
        self.btn_tts_generate_play.setEnabled(True)
        self.btn_tts_save_audio.setEnabled(bool(self._tts_last_audio))
        if not self._tts_last_audio:
            self.statusBar().showMessage("TTS returned empty audio")
            return
        try:
            play_wav_bytes(self._tts_last_audio)
            self.statusBar().showMessage("Speech generated and playing")
        except Exception as e:
            self.statusBar().showMessage(f"TTS generated (playback failed): {e}")

    def _save_last_tts_audio(self):
        if not self._tts_last_audio:
            self.statusBar().showMessage("No TTS audio to save")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save TTS Audio", "tts_output.wav", "WAV Audio (*.wav);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(self._tts_last_audio)
            self.statusBar().showMessage("TTS audio saved")
        except OSError as e:
            self.statusBar().showMessage(f"Failed to save audio: {e}")

    def _on_tts_error(self, err: str):
        logger.error("TTS failed: %s", err)
        self.btn_tts_generate_play.setEnabled(True)
        self.statusBar().showMessage(f"TTS failed: {err}")

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

    # ── Window close → quit app/process ───────────────────────────
    def closeEvent(self, event):
        event.accept()
        app = QApplication.instance()
        if app:
            app.quit()
