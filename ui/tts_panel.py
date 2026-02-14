"""Text-to-Speech input panel widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QStyle,
)
from PyQt6.QtCore import pyqtSignal


class TTSPanel(QWidget):
    """Text-to-Speech input and playback controls."""

    generate_requested = pyqtSignal(str)
    use_output_requested = pyqtSignal()
    save_audio_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.tts_input = QTextEdit()
        self.tts_input.setPlaceholderText("Enter text to synthesize, or load from transcription output.")
        layout.addWidget(self.tts_input)

        btn_row = QHBoxLayout()
        self.btn_from_output = QPushButton("Use Transcription Output")
        self.btn_generate_play = QPushButton("Generate & Play")
        self.btn_save_audio = QPushButton("Save Last Audio")
        self.btn_save_audio.setEnabled(False)
        self.btn_from_output.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.btn_generate_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_save_audio.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))

        self.btn_from_output.clicked.connect(self.use_output_requested.emit)
        self.btn_generate_play.clicked.connect(self._on_generate)
        self.btn_save_audio.clicked.connect(self.save_audio_requested.emit)

        btn_row.addWidget(self.btn_from_output)
        btn_row.addWidget(self.btn_generate_play)
        btn_row.addWidget(self.btn_save_audio)
        layout.addLayout(btn_row)
        layout.addStretch()

    def _on_generate(self):
        text = self.tts_input.toPlainText().strip()
        if text:
            self.generate_requested.emit(text)

    def set_text(self, text: str):
        self.tts_input.setPlainText(text)

    def set_generate_enabled(self, enabled: bool):
        self.btn_generate_play.setEnabled(enabled)

    def set_save_enabled(self, enabled: bool):
        self.btn_save_audio.setEnabled(enabled)
