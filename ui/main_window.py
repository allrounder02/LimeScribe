from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from core.lemonfox_client import LemonFoxClient
from core.audio_recorder import AudioRecorder
from core.vad_listener import VADListener
from core.text_output import copy_to_clipboard, paste_to_active_window


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

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_listening_tab(), "Listening")
        self.tabs.addTab(self._build_recording_tab(), "Recording")
        self.tabs.addTab(self._build_file_tab(), "File")
        layout.addWidget(self.tabs)

        # Shared output area
        self.output_label = QLabel("Transcription Output:")
        layout.addWidget(self.output_label)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        # Copy button
        btn_row = QHBoxLayout()
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self._copy_output)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_copy)
        layout.addLayout(btn_row)

        # Status bar
        self.statusBar().showMessage("Ready")

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
            self.btn_listen_toggle.setText("Stop Listening")
            self.statusBar().showMessage("Listening (VAD)...")
            self._start_listening()
        else:
            self.btn_listen_toggle.setText("Start Listening")
            self.statusBar().showMessage("Ready")
            self._stop_listening()

    def _start_listening(self):
        if self.tray:
            self.tray.set_state("listening")
        self._vad = VADListener(on_speech_chunk=self._on_vad_chunk)
        self._vad.start()

    def _stop_listening(self):
        if self._vad:
            self._vad.stop()
            self._vad = None
        if self.tray:
            self.tray.set_state("idle")

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
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("Copied to clipboard")

    # ── Window close → hide to tray ───────────────────────────────
    def closeEvent(self, event):
        event.ignore()
        self.hide()
