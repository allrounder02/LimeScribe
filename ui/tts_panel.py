"""Text-to-Speech input panel widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QSlider, QDoubleSpinBox, QComboBox,
    QCheckBox, QSpinBox, QToolButton, QAbstractSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.icon_library import ui_icon


class TTSPanel(QWidget):
    """Text-to-Speech input and playback controls."""

    generate_requested = pyqtSignal(str)
    optimization_settings_changed = pyqtSignal(bool, int)
    use_output_requested = pyqtSignal()
    save_audio_requested = pyqtSignal()
    open_saved_audio_requested = pyqtSignal()
    tts_profile_selected = pyqtSignal(str)
    play_pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(float)
    speed_changed = pyqtSignal(float)
    pitch_changed = pyqtSignal(float)
    api_speed_changed = pyqtSignal(float)

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

        api_speed_row = QHBoxLayout()
        api_speed_row.addWidget(QLabel("API Speed"))
        self.input_api_speed = QDoubleSpinBox()
        self.input_api_speed.setDecimals(2)
        self.input_api_speed.setRange(0.25, 4.00)
        self.input_api_speed.setSingleStep(0.05)
        self.input_api_speed.setValue(1.00)
        self.input_api_speed.setToolTip(
            "Applied when you click Generate & Play. This changes synthesis speed before API call."
        )
        self.input_api_speed.valueChanged.connect(self._on_api_speed_value_changed)
        api_speed_row.addWidget(self.input_api_speed)
        api_speed_row.addStretch()
        layout.addLayout(api_speed_row)

        optimization_row = QHBoxLayout()
        self.chk_optimize_long_text = QCheckBox("Optimize long text punctuation")
        self.chk_optimize_long_text.setChecked(True)
        self.chk_optimize_long_text.setToolTip(
            "When enabled, long text is cleaned and sentence-broken for better pronunciation."
        )
        self.chk_optimize_long_text.toggled.connect(self._emit_optimization_settings_changed)
        optimization_row.addWidget(self.chk_optimize_long_text)
        optimization_row.addWidget(QLabel("Threshold (chars)"))
        self.input_optimize_threshold = QSpinBox()
        self.input_optimize_threshold.setRange(80, 5000)
        self.input_optimize_threshold.setSingleStep(20)
        self.input_optimize_threshold.setValue(240)
        self.input_optimize_threshold.setToolTip(
            "Apply optimization only when input length reaches this many characters."
        )
        self.input_optimize_threshold.valueChanged.connect(self._emit_optimization_settings_changed)
        optimization_row.addWidget(self.input_optimize_threshold)
        optimization_row.addStretch()
        layout.addLayout(optimization_row)

        btn_row = QHBoxLayout()
        self.btn_from_output = QPushButton("Use Transcription Output")
        self.btn_generate_play = QPushButton("Generate & Play")
        self.btn_save_audio = QPushButton("Save Last Audio")
        self.btn_open_saved_audio = QPushButton("Open Saved Audio")
        self.btn_save_audio.setEnabled(False)
        self.btn_from_output.setIcon(ui_icon(self, "tts_use_output"))
        self.btn_generate_play.setIcon(ui_icon(self, "tts_generate_play"))
        self.btn_save_audio.setIcon(ui_icon(self, "tts_save_audio"))
        self.btn_open_saved_audio.setIcon(ui_icon(self, "tts_open_saved_audio"))

        self.btn_from_output.clicked.connect(self.use_output_requested.emit)
        self.btn_generate_play.clicked.connect(self._on_generate)
        self.btn_save_audio.clicked.connect(self.save_audio_requested.emit)
        self.btn_open_saved_audio.clicked.connect(self.open_saved_audio_requested.emit)

        btn_row.addWidget(self.btn_from_output)
        btn_row.addWidget(self.btn_generate_play)
        btn_row.addWidget(self.btn_save_audio)
        btn_row.addWidget(self.btn_open_saved_audio)
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
        tuning_row.addWidget(QLabel("Playback Speed"))
        self.btn_speed_down = QToolButton()
        self.btn_speed_down.setText("-")
        self.btn_speed_down.setToolTip("Decrease playback speed")
        self.btn_speed_down.setProperty("role", "tts-adjust")
        self.btn_speed_down.clicked.connect(lambda: self._step_speed(-1))
        tuning_row.addWidget(self.btn_speed_down)

        self.input_playback_speed = QDoubleSpinBox()
        self.input_playback_speed.setDecimals(2)
        self.input_playback_speed.setRange(0.50, 2.50)
        self.input_playback_speed.setSingleStep(0.05)
        self.input_playback_speed.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.input_playback_speed.setValue(1.00)
        self.input_playback_speed.valueChanged.connect(self._on_speed_value_changed)
        self.input_playback_speed.setToolTip(
            "Playback-only speed multiplier (0.50x to 2.50x). API synth speed is in Settings > Voice."
        )
        tuning_row.addWidget(self.input_playback_speed)

        self.btn_speed_up = QToolButton()
        self.btn_speed_up.setText("+")
        self.btn_speed_up.setToolTip("Increase playback speed")
        self.btn_speed_up.setProperty("role", "tts-adjust")
        self.btn_speed_up.clicked.connect(lambda: self._step_speed(1))
        tuning_row.addWidget(self.btn_speed_up)

        tuning_row.addWidget(QLabel("Playback Pitch"))
        self.btn_pitch_down = QToolButton()
        self.btn_pitch_down.setText("-")
        self.btn_pitch_down.setToolTip("Decrease playback pitch")
        self.btn_pitch_down.setProperty("role", "tts-adjust")
        self.btn_pitch_down.clicked.connect(lambda: self._step_pitch(-1))
        tuning_row.addWidget(self.btn_pitch_down)

        self.input_playback_pitch = QDoubleSpinBox()
        self.input_playback_pitch.setDecimals(1)
        self.input_playback_pitch.setRange(-12.0, 12.0)
        self.input_playback_pitch.setSingleStep(0.5)
        self.input_playback_pitch.setSuffix(" st")
        self.input_playback_pitch.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.input_playback_pitch.setValue(0.0)
        self.input_playback_pitch.valueChanged.connect(self._on_pitch_value_changed)
        self.input_playback_pitch.setToolTip(
            "Playback-only pitch in semitones (-12 to +12). Does not change API voice/language."
        )
        tuning_row.addWidget(self.input_playback_pitch)

        self.btn_pitch_up = QToolButton()
        self.btn_pitch_up.setText("+")
        self.btn_pitch_up.setToolTip("Increase playback pitch")
        self.btn_pitch_up.setProperty("role", "tts-adjust")
        self.btn_pitch_up.clicked.connect(lambda: self._step_pitch(1))
        tuning_row.addWidget(self.btn_pitch_up)
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
        self.btn_speed_down.setEnabled(available)
        self.btn_speed_up.setEnabled(available)
        self.btn_pitch_down.setEnabled(available)
        self.btn_pitch_up.setEnabled(available)
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

    def get_api_speed(self) -> float:
        return float(self.input_api_speed.value())

    def set_api_speed(self, speed: float, emit: bool = False):
        value = self._coerce_api_speed(speed)
        self.input_api_speed.blockSignals(True)
        self.input_api_speed.setValue(value)
        self.input_api_speed.blockSignals(False)
        if emit:
            self.api_speed_changed.emit(value)

    def should_optimize_long_text(self) -> bool:
        return bool(self.chk_optimize_long_text.isChecked())

    def get_optimize_threshold_chars(self) -> int:
        return int(self.input_optimize_threshold.value())

    def set_long_text_optimization(self, enabled: bool, threshold_chars: int, emit: bool = False):
        self.chk_optimize_long_text.blockSignals(True)
        self.input_optimize_threshold.blockSignals(True)
        self.chk_optimize_long_text.setChecked(bool(enabled))
        self.input_optimize_threshold.setValue(int(threshold_chars))
        self.chk_optimize_long_text.blockSignals(False)
        self.input_optimize_threshold.blockSignals(False)
        if emit:
            self._emit_optimization_settings_changed()

    def _emit_optimization_settings_changed(self, *_args):
        self.optimization_settings_changed.emit(
            self.should_optimize_long_text(),
            self.get_optimize_threshold_chars(),
        )

    def _on_speed_value_changed(self, value: float):
        self.speed_changed.emit(float(value))

    def _on_pitch_value_changed(self, value: float):
        self.pitch_changed.emit(float(value))

    def _on_api_speed_value_changed(self, value: float):
        self.api_speed_changed.emit(float(value))

    def _step_speed(self, direction: int):
        if direction >= 0:
            self.input_playback_speed.stepUp()
            return
        self.input_playback_speed.stepDown()

    def _step_pitch(self, direction: int):
        if direction >= 0:
            self.input_playback_pitch.stepUp()
            return
        self.input_playback_pitch.stepDown()

    @staticmethod
    def _coerce_api_speed(value) -> float:
        try:
            speed = float(value)
        except (TypeError, ValueError):
            speed = 1.0
        if speed <= 0:
            speed = 1.0
        return max(0.25, min(4.0, speed))
