from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog, QLineEdit, QMessageBox, QApplication,
    QSystemTrayIcon,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.lemonfox_client import LemonFoxClient
from core.audio_recorder import AudioRecorder
from core.vad_listener import VADListener
from core.text_output import copy_to_clipboard, paste_to_active_window
from hotkeys import DEFAULT_HOTKEY_LISTEN, DEFAULT_HOTKEY_RECORD


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


class MainWindow(QMainWindow):
    """Main application window with Listening / Recording / File tabs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LemonFox Transcriber")
        self.setMinimumSize(500, 400)

        self.client = LemonFoxClient()
        self.recorder = AudioRecorder()
        self.tray = None  # Set by app.py after construction
        self._worker = None
        self._vad = None
        self._listen_workers = []  # keep refs so they don't get GC'd
        self.hotkeys = None
        self._on_hotkeys_changed = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_listening_tab(), "Listening")
        self.tabs.addTab(self._build_recording_tab(), "Recording")
        self.tabs.addTab(self._build_file_tab(), "File")
        self.tabs.addTab(self._build_settings_tab(), "Settings")
        layout.addWidget(self.tabs)

        # Shared output area
        self.output_label = QLabel("Transcription Output:")
        layout.addWidget(self.output_label)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        # Output actions
        btn_row = QHBoxLayout()
        self.btn_minimize_tray = QPushButton("Minimize to Tray")
        self.btn_minimize_tray.clicked.connect(self._minimize_to_tray)
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self._clear_output)
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy_output)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_minimize_tray)
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
        current = self.text_output.toPlainText()
        separator = " " if current else ""
        full_text = current + separator + text
        self.text_output.setPlainText(full_text)
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

    # ── Shared transcription logic ─────────────────────────────────
    def _run_transcription(self, audio_bytes=None, file_path=None):
        self._worker = TranscribeWorker(self.client, audio_bytes=audio_bytes, file_path=file_path)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_transcription_error)
        self._worker.start()

    def _on_transcription_done(self, text):
        self.text_output.setPlainText(text)
        copy_to_clipboard(text)
        self.statusBar().showMessage("Transcription complete — copied to clipboard")

    def _on_transcription_error(self, err):
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
