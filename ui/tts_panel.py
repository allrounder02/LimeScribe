"""Text-to-Speech input panel widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QSlider, QDoubleSpinBox, QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.icon_library import ui_icon


class TTSPanel(QWidget):
    """Text-to-Speech input and playback controls."""

    generate_requested = pyqtSignal(str)
    use_output_requested = pyqtSignal()
    save_audio_requested = pyqtSignal()
    tts_profile_selected = pyqtSignal(str)
    play_pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(float)
    speed_changed = pyqtSignal(float)
    pitch_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._duration_seconds = 0.0
        self._slider_tracking = False
        self._updating_profile_combo = False

        layout = QVBoxLayout(self)

        self.tts_input = QTextEdit()
        self.tts_input.setPlaceholderText("Enter text to synthesize, or load from transcription output.")
        layout.addWidget(self.tts_input)

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Voice Profile"))
        self.combo_tts_profiles = QComboBox()
        self.combo_tts_profiles.setEditable(False)
        self.combo_tts_profiles.currentTextChanged.connect(self._on_tts_profile_changed)
        profile_row.addWidget(self.combo_tts_profiles, 1)
        layout.addLayout(profile_row)

        btn_row = QHBoxLayout()
        self.btn_from_output = QPushButton("Use Transcription Output")
        self.btn_generate_play = QPushButton("Generate & Play")
        self.btn_save_audio = QPushButton("Save Last Audio")
        self.btn_save_audio.setEnabled(False)
        self.btn_from_output.setIcon(ui_icon(self, "tts_use_output"))
        self.btn_generate_play.setIcon(ui_icon(self, "tts_generate_play"))
        self.btn_save_audio.setIcon(ui_icon(self, "tts_save_audio"))

        self.btn_from_output.clicked.connect(self.use_output_requested.emit)
        self.btn_generate_play.clicked.connect(self._on_generate)
        self.btn_save_audio.clicked.connect(self.save_audio_requested.emit)

        btn_row.addWidget(self.btn_from_output)
        btn_row.addWidget(self.btn_generate_play)
        btn_row.addWidget(self.btn_save_audio)
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("Playback"))

        transport_row = QHBoxLayout()
        self.btn_play_pause = QPushButton("Play")
        self.btn_stop = QPushButton("Stop")
        self.btn_play_pause.clicked.connect(self.play_pause_requested.emit)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        transport_row.addWidget(self.btn_play_pause)
        transport_row.addWidget(self.btn_stop)

        self.lbl_position = QLabel("00:00")
        transport_row.addWidget(self.lbl_position)

        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setRange(0, 0)
        self.slider_position.sliderPressed.connect(self._on_slider_pressed)
        self.slider_position.sliderMoved.connect(self._on_slider_moved)
        self.slider_position.sliderReleased.connect(self._on_slider_released)
        transport_row.addWidget(self.slider_position, 1)

        self.lbl_duration = QLabel("00:00")
        transport_row.addWidget(self.lbl_duration)
        layout.addLayout(transport_row)

        tuning_row = QHBoxLayout()
        tuning_row.addWidget(QLabel("Speed"))
        self.input_playback_speed = QDoubleSpinBox()
        self.input_playback_speed.setDecimals(2)
        self.input_playback_speed.setRange(0.50, 2.50)
        self.input_playback_speed.setSingleStep(0.05)
        self.input_playback_speed.setValue(1.00)
        self.input_playback_speed.valueChanged.connect(lambda v: self.speed_changed.emit(float(v)))
        tuning_row.addWidget(self.input_playback_speed)

        tuning_row.addWidget(QLabel("Pitch"))
        self.input_playback_pitch = QDoubleSpinBox()
        self.input_playback_pitch.setDecimals(1)
        self.input_playback_pitch.setRange(-12.0, 12.0)
        self.input_playback_pitch.setSingleStep(0.5)
        self.input_playback_pitch.setSuffix(" st")
        self.input_playback_pitch.setValue(0.0)
        self.input_playback_pitch.valueChanged.connect(lambda v: self.pitch_changed.emit(float(v)))
        tuning_row.addWidget(self.input_playback_pitch)
        tuning_row.addStretch()
        layout.addLayout(tuning_row)

        self.set_playback_available(False)
        layout.addStretch()

    def _on_generate(self):
        text = self.tts_input.toPlainText().strip()
        if text:
            self.generate_requested.emit(text)

    def _on_tts_profile_changed(self, name: str):
        if self._updating_profile_combo:
            return
        selected = (name or "").strip()
        if selected:
            self.tts_profile_selected.emit(selected)

    @staticmethod
    def _format_mm_ss(seconds: float) -> str:
        total = max(0, int(round(seconds)))
        minutes = total // 60
        secs = total % 60
        return f"{minutes:02d}:{secs:02d}"

    def _on_slider_pressed(self):
        self._slider_tracking = True

    def _on_slider_moved(self, value: int):
        self.lbl_position.setText(self._format_mm_ss(value / 1000.0))

    def _on_slider_released(self):
        self._slider_tracking = False
        self.seek_requested.emit(self.slider_position.value() / 1000.0)

    def set_text(self, text: str):
        self.tts_input.setPlainText(text)

    def set_tts_profiles(self, profiles: list[dict], active_name: str):
        names = [str(p.get("name", "")).strip() for p in profiles if isinstance(p, dict) and str(p.get("name", "")).strip()]
        self._updating_profile_combo = True
        self.combo_tts_profiles.clear()
        for name in names:
            self.combo_tts_profiles.addItem(name)
        idx = self.combo_tts_profiles.findText(active_name)
        self.combo_tts_profiles.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_tts_profiles.setEnabled(bool(names))
        self._updating_profile_combo = False

    def set_active_tts_profile(self, profile_name: str):
        name = (profile_name or "").strip()
        if not name:
            return
        idx = self.combo_tts_profiles.findText(name)
        if idx < 0:
            return
        self._updating_profile_combo = True
        self.combo_tts_profiles.setCurrentIndex(idx)
        self._updating_profile_combo = False

    def set_generate_enabled(self, enabled: bool):
        self.btn_generate_play.setEnabled(enabled)

    def set_save_enabled(self, enabled: bool):
        self.btn_save_audio.setEnabled(enabled)

    def set_playback_available(self, available: bool):
        self.btn_play_pause.setEnabled(available)
        self.btn_stop.setEnabled(available)
        self.slider_position.setEnabled(available)
        self.input_playback_speed.setEnabled(available)
        self.input_playback_pitch.setEnabled(available)
        if not available:
            self.set_playing(False)
            self.set_duration(0.0)
            self.set_position(0.0)

    def set_playing(self, playing: bool):
        self.btn_play_pause.setText("Pause" if playing else "Play")

    def set_duration(self, seconds: float):
        self._duration_seconds = max(0.0, float(seconds))
        self.slider_position.setRange(0, int(round(self._duration_seconds * 1000)))
        self.lbl_duration.setText(self._format_mm_ss(self._duration_seconds))

    def set_position(self, seconds: float):
        position = max(0.0, min(self._duration_seconds, float(seconds)))
        self.lbl_position.setText(self._format_mm_ss(position))
        if self._slider_tracking:
            return
        self.slider_position.blockSignals(True)
        self.slider_position.setValue(int(round(position * 1000)))
        self.slider_position.blockSignals(False)

    def get_playback_speed(self) -> float:
        return float(self.input_playback_speed.value())

    def get_playback_pitch(self) -> float:
        return float(self.input_playback_pitch.value())
