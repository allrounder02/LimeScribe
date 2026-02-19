"""Settings panel widget — General, Speech, Voice sub-tabs + profiles."""

import json
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox,
    QSlider, QSpinBox, QDoubleSpinBox,
    QScrollArea, QMessageBox, QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from hotkeys import DEFAULT_HOTKEY_LISTEN, DEFAULT_HOTKEY_RECORD
from ui.icon_library import ui_icon
from config import (
    LEMONFOX_LANGUAGE,
    LEMONFOX_RESPONSE_FORMAT,
    VAD_AGGRESSIVENESS,
    VAD_MIN_SPEECH_SECONDS,
    LEMONFOX_TTS_MODEL,
    LEMONFOX_TTS_VOICE,
    LEMONFOX_TTS_LANGUAGE,
    LEMONFOX_TTS_RESPONSE_FORMAT,
    LEMONFOX_TTS_SPEED,
)

logger = logging.getLogger(__name__)

TTS_MODEL_PRESETS = ["tts-1", "tts-1-hd"]
TTS_LANGUAGE_PRESETS = ["en-us", "en-gb", "ja", "zh", "es", "fr", "hi", "it", "pt-br"]
TTS_RESPONSE_FORMAT_PRESETS = ["wav", "mp3", "ogg", "flac"]
STT_RESPONSE_FORMAT_PRESETS = ["json", "text", "srt", "vtt"]
STT_LANGUAGE_PRESETS = ["english", "german", "spanish", "italian", "french"]
VOICE_PRESETS_PATH = Path(__file__).resolve().parent.parent / "data" / "voice_presets.json"
VAD_NOISE_MIN = 0
VAD_NOISE_MAX = 100
VAD_MIN_SPEECH_FLOOR = 0.30
VAD_MIN_SPEECH_CEIL = 1.20
TTS_SPEED_MIN = 0.25
TTS_SPEED_MAX = 4.00
VAD_NOISE_DEFAULT = int(
    round(
        (
            (max(0.0, min(1.0, float(VAD_AGGRESSIVENESS) / 3.0)) * 0.7)
            + (max(0.0, min(1.0, ((float(VAD_MIN_SPEECH_SECONDS) - 0.30) / (1.20 - 0.30)))) * 0.3)
        )
        * 100
    )
)


class SettingsPanel(QWidget):
    """Settings panel with General, Speech, and Voice sub-tabs."""

    hotkeys_save_requested = pyqtSignal(str, str)  # listen_hotkey, record_hotkey
    stt_settings_changed = pyqtSignal(dict)
    tts_settings_changed = pyqtSignal(dict)
    profiles_changed = pyqtSignal(dict)
    tts_profiles_changed = pyqtSignal(dict)
    ui_settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._voice_presets = self._load_voice_presets()
        self._profiles = []
        self._tts_profiles = []
        self.hotkeys = None
        self._updating_vad_controls = False
        self._updating_tts_controls = False
        self._stt_auto_apply_timer = QTimer(self)
        self._stt_auto_apply_timer.setSingleShot(True)
        self._stt_auto_apply_timer.timeout.connect(lambda: self._emit_stt_settings(show_status=False))
        self._tts_auto_apply_timer = QTimer(self)
        self._tts_auto_apply_timer.setSingleShot(True)
        self._tts_auto_apply_timer.timeout.connect(lambda: self._emit_tts_settings(show_status=False, silent=True))

        layout = QVBoxLayout(self)
        self._pages = QTabWidget()
        self._pages.addTab(self._wrap_in_scroll(self._build_general_page()), "General")
        self._pages.addTab(self._wrap_in_scroll(self._build_speech_page()), "Speech")
        self._pages.addTab(self._wrap_in_scroll(self._build_voice_page()), "Voice")
        layout.addWidget(self._pages)

    # ── Public API ─────────────────────────────────────────────────

    def attach_hotkey_manager(self, hotkeys, listen_hotkey: str, record_hotkey: str):
        self.hotkeys = hotkeys
        self.input_listen_hotkey.setText(listen_hotkey)
        self.input_record_hotkey.setText(record_hotkey)

    def apply_stt_settings(
        self,
        language: str,
        response_format: str,
        auto_copy: bool,
        clear_output_after_copy: bool = False,
        stop_listening_after_copy: bool = False,
        keep_wrapping_parentheses: bool = False,
        vad_noise_level=None,
        vad_aggressiveness=None,
        vad_min_speech_seconds=None,
    ):
        self._set_combo_value(self.input_stt_language, language)
        self._set_combo_value(self.input_stt_response_format, response_format)
        self.chk_auto_copy_transcription.setChecked(auto_copy)
        self.chk_clear_output_after_copy.setChecked(bool(clear_output_after_copy))
        self.chk_stop_listening_after_copy.setChecked(bool(stop_listening_after_copy))
        self.chk_keep_wrapping_parentheses.setChecked(bool(keep_wrapping_parentheses))
        aggr = self._clamp_aggressiveness(vad_aggressiveness if vad_aggressiveness is not None else VAD_AGGRESSIVENESS)
        min_speech = self._clamp_min_speech(
            vad_min_speech_seconds if vad_min_speech_seconds is not None else VAD_MIN_SPEECH_SECONDS
        )
        if vad_noise_level is None:
            noise = self._estimate_noise_level(aggr, min_speech)
        else:
            noise = self._clamp_noise(vad_noise_level)
        self._updating_vad_controls = True
        self.slider_vad_noise.setValue(noise)
        self.input_vad_aggressiveness.setValue(aggr)
        self.input_vad_min_speech_seconds.setValue(min_speech)
        self._updating_vad_controls = False
        self._update_vad_summary()
        self._emit_stt_settings(show_status=False)

    def apply_tts_settings(self, model: str, voice: str, language: str, response_format: str, speed: str):
        self._updating_tts_controls = True
        self._set_combo_value(self.input_tts_model, model)
        self._set_voice_combo_value(voice)
        self._set_combo_value(self.input_tts_language, language)
        self._set_combo_value(self.input_tts_response_format, response_format)
        self.input_tts_speed.setValue(self._coerce_tts_speed(speed))
        self._updating_tts_controls = False
        self._emit_tts_settings(show_status=False, silent=True)

    def set_tts_speed_value(self, speed: float, emit: bool = False):
        if not hasattr(self, "input_tts_speed"):
            return
        self._updating_tts_controls = True
        self.input_tts_speed.setValue(self._coerce_tts_speed(speed))
        self._updating_tts_controls = False
        if emit:
            self._emit_tts_settings(show_status=False, silent=True)

    def apply_ui_settings(self, dark_mode: bool):
        if not hasattr(self, "chk_dark_mode"):
            return
        self.chk_dark_mode.blockSignals(True)
        self.chk_dark_mode.setChecked(bool(dark_mode))
        self.chk_dark_mode.blockSignals(False)

    def apply_profiles(self, profiles: list, active_name: str):
        self._profiles = [dict(p) for p in profiles if isinstance(p, dict) and p.get("name")]
        if not self._profiles:
            self._profiles = [self._build_profile("Default")]
        self._refresh_profiles_combo()
        idx = self.combo_profiles.findText(active_name)
        self.combo_profiles.setCurrentIndex(idx if idx >= 0 else 0)
        active = self._find_profile_by_name(self.combo_profiles.currentText().strip())
        if active:
            self._apply_profile_to_ui(active)

    def apply_profile(self, profile: dict):
        if not isinstance(profile, dict):
            return
        self._apply_profile_to_ui(profile)

    def set_active_profile(self, profile_name: str):
        name = (profile_name or "").strip()
        if not name:
            return
        idx = self.combo_profiles.findText(name)
        if idx < 0:
            return
        self.combo_profiles.blockSignals(True)
        self.combo_profiles.setCurrentIndex(idx)
        self.combo_profiles.blockSignals(False)

    def apply_tts_profiles(self, profiles: list, active_name: str):
        self._tts_profiles = [dict(p) for p in profiles if isinstance(p, dict) and p.get("name")]
        if not self._tts_profiles:
            self._tts_profiles = [self._build_tts_profile("Default Voice")]
        self._refresh_tts_profiles_combo()
        idx = self.combo_tts_profiles.findText(active_name)
        self.combo_tts_profiles.setCurrentIndex(idx if idx >= 0 else 0)

    def apply_tts_profile(self, profile: dict, emit_tts: bool = False):
        if not isinstance(profile, dict):
            return
        self._apply_tts_profile_to_ui(profile, emit_tts=emit_tts)

    def set_active_tts_profile(self, profile_name: str):
        name = (profile_name or "").strip()
        if not name:
            return
        idx = self.combo_tts_profiles.findText(name)
        if idx < 0:
            return
        self.combo_tts_profiles.blockSignals(True)
        self.combo_tts_profiles.setCurrentIndex(idx)
        self.combo_tts_profiles.blockSignals(False)

    # ── Collect settings from UI ───────────────────────────────────

    def collect_stt_settings(self) -> dict:
        language = self.input_stt_language.currentText().strip().lower()
        response_format = self.input_stt_response_format.currentText().strip().lower()
        if not language or not response_format:
            raise ValueError("STT language and response format are required.")
        vad_noise_level = int(self.slider_vad_noise.value())
        vad_aggressiveness = int(self.input_vad_aggressiveness.value())
        vad_min_speech_seconds = float(self.input_vad_min_speech_seconds.value())
        return {
            "stt_language": language,
            "stt_response_format": response_format,
            "auto_copy_transcription": self.chk_auto_copy_transcription.isChecked(),
            "clear_output_after_copy": self.chk_clear_output_after_copy.isChecked(),
            "stop_listening_after_copy": self.chk_stop_listening_after_copy.isChecked(),
            "keep_wrapping_parentheses": self.chk_keep_wrapping_parentheses.isChecked(),
            "vad_noise_level": vad_noise_level,
            "vad_aggressiveness": vad_aggressiveness,
            "vad_min_speech_seconds": vad_min_speech_seconds,
        }

    def collect_tts_settings(self) -> dict:
        model = self.input_tts_model.currentText().strip()
        voice = self._current_voice_value()
        language = self.input_tts_language.currentText().strip()
        response_format = self.input_tts_response_format.currentText().strip().lower()

        if not model or not voice or not language or not response_format:
            raise ValueError("Model, voice, language, and response format are required.")
        speed = float(self.input_tts_speed.value())
        if speed <= 0:
            raise ValueError("Speed must be greater than 0.")

        return {
            "tts_model": model,
            "tts_voice": voice,
            "tts_language": language,
            "tts_response_format": response_format,
            "tts_speed": self._format_tts_speed(speed),
        }

    # ── Page builders ──────────────────────────────────────────────

    @staticmethod
    def _wrap_in_scroll(widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setObjectName("settingsScrollArea")
        widget.setObjectName("settingsScrollContent")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(widget)
        return scroll

    def _build_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
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
        self.btn_hotkeys_save.setIcon(ui_icon(self, "settings_hotkeys_save"))
        self.btn_hotkeys_defaults.setIcon(ui_icon(self, "settings_hotkeys_defaults"))
        self.btn_hotkeys_save.clicked.connect(self._save_hotkeys)
        self.btn_hotkeys_defaults.clicked.connect(self._restore_default_hotkeys)
        btn_row.addWidget(self.btn_hotkeys_save)
        btn_row.addWidget(self.btn_hotkeys_defaults)
        layout.addLayout(btn_row)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Appearance"))
        self.chk_dark_mode = QCheckBox("Enable dark mode")
        self.chk_dark_mode.setChecked(False)
        self.chk_dark_mode.toggled.connect(lambda _v: self._emit_ui_settings())
        layout.addWidget(self.chk_dark_mode)
        layout.addStretch()
        return page

    def _build_speech_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Speech-to-Text"))

        stt_lang_row = QHBoxLayout()
        stt_lang_row.addWidget(QLabel("Language:"))
        self.input_stt_language = QComboBox()
        self.input_stt_language.setEditable(True)
        self.input_stt_language.addItems(STT_LANGUAGE_PRESETS)
        self.input_stt_language.setCurrentText(LEMONFOX_LANGUAGE)
        self.input_stt_language.currentTextChanged.connect(lambda _v: self._schedule_stt_auto_apply())
        stt_lang_row.addWidget(self.input_stt_language)
        layout.addLayout(stt_lang_row)

        stt_fmt_row = QHBoxLayout()
        stt_fmt_row.addWidget(QLabel("Response Format:"))
        self.input_stt_response_format = QComboBox()
        self.input_stt_response_format.setEditable(True)
        self.input_stt_response_format.addItems(STT_RESPONSE_FORMAT_PRESETS)
        self.input_stt_response_format.setCurrentText(LEMONFOX_RESPONSE_FORMAT)
        self.input_stt_response_format.currentTextChanged.connect(lambda _v: self._schedule_stt_auto_apply())
        stt_fmt_row.addWidget(self.input_stt_response_format)
        layout.addLayout(stt_fmt_row)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Listening (VAD)"))
        layout.addWidget(QLabel("Use the noise slider for auto-tuning, then fine-tune manually if needed."))
        vad_quick_guide = QLabel(
            "Quick guide: lower slider = quieter environment (less strict); higher slider = noisier environment "
            "(more strict noise filtering)."
        )
        vad_quick_guide.setWordWrap(True)
        layout.addWidget(vad_quick_guide)

        noise_row = QHBoxLayout()
        noise_row.addWidget(QLabel("Noise Auto-Tune:"))
        self.slider_vad_noise = QSlider(Qt.Orientation.Horizontal)
        self.slider_vad_noise.setRange(VAD_NOISE_MIN, VAD_NOISE_MAX)
        self.slider_vad_noise.setSingleStep(1)
        self.slider_vad_noise.setPageStep(5)
        self.slider_vad_noise.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_vad_noise.setTickInterval(10)
        self.slider_vad_noise.setToolTip(
            "Lower = quieter room and less strict filtering. Higher = noisier room and stricter filtering."
        )
        self.slider_vad_noise.valueChanged.connect(self._on_noise_slider_changed)
        noise_row.addWidget(self.slider_vad_noise, 1)
        self.lbl_vad_noise_value = QLabel("0")
        noise_row.addWidget(self.lbl_vad_noise_value)
        layout.addLayout(noise_row)

        vad_aggr_row = QHBoxLayout()
        vad_aggr_row.addWidget(QLabel("VAD Aggressiveness (0-3):"))
        self.input_vad_aggressiveness = QSpinBox()
        self.input_vad_aggressiveness.setRange(0, 3)
        self.input_vad_aggressiveness.setValue(VAD_AGGRESSIVENESS)
        self.input_vad_aggressiveness.setToolTip(
            "Higher aggressiveness removes more background noise, but can miss soft/quiet speech."
        )
        self.input_vad_aggressiveness.valueChanged.connect(self._on_manual_vad_changed)
        vad_aggr_row.addWidget(self.input_vad_aggressiveness)
        layout.addLayout(vad_aggr_row)
        vad_aggr_hint = QLabel(
            "Hint: higher aggressiveness = stronger noise rejection; lower aggressiveness = catches softer speech."
        )
        vad_aggr_hint.setWordWrap(True)
        layout.addWidget(vad_aggr_hint)

        vad_min_row = QHBoxLayout()
        vad_min_row.addWidget(QLabel("VAD Min Speech Seconds:"))
        self.input_vad_min_speech_seconds = QDoubleSpinBox()
        self.input_vad_min_speech_seconds.setRange(0.10, 3.00)
        self.input_vad_min_speech_seconds.setSingleStep(0.05)
        self.input_vad_min_speech_seconds.setDecimals(2)
        self.input_vad_min_speech_seconds.setValue(VAD_MIN_SPEECH_SECONDS)
        self.input_vad_min_speech_seconds.setToolTip(
            "Lower values send short phrases faster. Higher values wait for longer speech and reduce tiny fragments."
        )
        self.input_vad_min_speech_seconds.valueChanged.connect(self._on_manual_vad_changed)
        vad_min_row.addWidget(self.input_vad_min_speech_seconds)
        layout.addLayout(vad_min_row)
        vad_min_hint = QLabel(
            "Hint: lower seconds = faster response; higher seconds = fewer accidental short transcriptions."
        )
        vad_min_hint.setWordWrap(True)
        layout.addWidget(vad_min_hint)

        self.lbl_vad_summary = QLabel("")
        layout.addWidget(self.lbl_vad_summary)
        self._updating_vad_controls = True
        self.slider_vad_noise.setValue(self._estimate_noise_level(VAD_AGGRESSIVENESS, VAD_MIN_SPEECH_SECONDS))
        self._updating_vad_controls = False
        self._update_vad_summary()

        stt_btn_row = QHBoxLayout()
        self.btn_stt_settings_save = QPushButton("Save STT Settings")
        self.btn_stt_settings_defaults = QPushButton("Restore STT Defaults")
        self.btn_stt_settings_save.setIcon(ui_icon(self, "settings_stt_save"))
        self.btn_stt_settings_defaults.setIcon(ui_icon(self, "settings_stt_defaults"))
        self.btn_stt_settings_save.clicked.connect(self._emit_stt_settings)
        self.btn_stt_settings_defaults.clicked.connect(self._restore_default_stt_settings)
        stt_btn_row.addWidget(self.btn_stt_settings_save)
        stt_btn_row.addWidget(self.btn_stt_settings_defaults)
        layout.addLayout(stt_btn_row)

        self.chk_auto_copy_transcription = QCheckBox("Auto-copy transcription to clipboard")
        self.chk_auto_copy_transcription.setChecked(True)
        self.chk_auto_copy_transcription.toggled.connect(lambda _v: self._schedule_stt_auto_apply())
        layout.addWidget(self.chk_auto_copy_transcription)
        self.chk_clear_output_after_copy = QCheckBox("Clear output after copying to clipboard")
        self.chk_clear_output_after_copy.setChecked(False)
        self.chk_clear_output_after_copy.toggled.connect(lambda _v: self._schedule_stt_auto_apply())
        layout.addWidget(self.chk_clear_output_after_copy)
        self.chk_stop_listening_after_copy = QCheckBox("Stop listening after copy to clipboard")
        self.chk_stop_listening_after_copy.setChecked(False)
        self.chk_stop_listening_after_copy.toggled.connect(lambda _v: self._schedule_stt_auto_apply())
        layout.addWidget(self.chk_stop_listening_after_copy)
        self.chk_keep_wrapping_parentheses = QCheckBox("Keep wrapping parentheses in transcription output")
        self.chk_keep_wrapping_parentheses.setChecked(False)
        self.chk_keep_wrapping_parentheses.toggled.connect(lambda _v: self._schedule_stt_auto_apply())
        layout.addWidget(self.chk_keep_wrapping_parentheses)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Profiles"))
        layout.addWidget(QLabel("Save and reuse named STT/TTS setting presets"))

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Profile:"))
        self.combo_profiles = QComboBox()
        self.combo_profiles.setEditable(False)
        profile_row.addWidget(self.combo_profiles)
        layout.addLayout(profile_row)

        profile_btn_row = QHBoxLayout()
        self.btn_profile_apply = QPushButton("Apply Profile")
        self.btn_profile_save_new = QPushButton("Save as New")
        self.btn_profile_update = QPushButton("Update Current")
        self.btn_profile_delete = QPushButton("Delete")
        self.btn_profile_apply.setIcon(ui_icon(self, "settings_profile_apply"))
        self.btn_profile_save_new.setIcon(ui_icon(self, "settings_profile_save_new"))
        self.btn_profile_update.setIcon(ui_icon(self, "settings_profile_update"))
        self.btn_profile_delete.setIcon(ui_icon(self, "settings_profile_delete"))
        self.btn_profile_apply.clicked.connect(self._apply_selected_profile)
        self.btn_profile_save_new.clicked.connect(self._save_profile_as_new)
        self.btn_profile_update.clicked.connect(self._update_selected_profile)
        self.btn_profile_delete.clicked.connect(self._delete_selected_profile)
        profile_btn_row.addWidget(self.btn_profile_apply)
        profile_btn_row.addWidget(self.btn_profile_save_new)
        profile_btn_row.addWidget(self.btn_profile_update)
        profile_btn_row.addWidget(self.btn_profile_delete)
        layout.addLayout(profile_btn_row)

        layout.addStretch()
        return page

    def _build_voice_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Voice Presets"))
        layout.addWidget(QLabel("Filter by language and gender, then select a voice actor."))

        filter_lang_row = QHBoxLayout()
        filter_lang_row.addWidget(QLabel("Preset Language:"))
        self.combo_voice_filter_language = QComboBox()
        self.combo_voice_filter_language.addItem("Any")
        for code in self._voice_languages():
            self.combo_voice_filter_language.addItem(code)
        self.combo_voice_filter_language.currentTextChanged.connect(self._refresh_voice_actor_options)
        filter_lang_row.addWidget(self.combo_voice_filter_language)
        layout.addLayout(filter_lang_row)

        filter_gender_row = QHBoxLayout()
        filter_gender_row.addWidget(QLabel("Preset Gender:"))
        self.combo_voice_filter_gender = QComboBox()
        self.combo_voice_filter_gender.addItems(["Any", "female", "male", "neutral"])
        self.combo_voice_filter_gender.currentTextChanged.connect(self._refresh_voice_actor_options)
        filter_gender_row.addWidget(self.combo_voice_filter_gender)
        layout.addLayout(filter_gender_row)

        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voice Actor:"))
        self.input_tts_voice = QComboBox()
        self.input_tts_voice.setEditable(True)
        self.input_tts_voice.currentIndexChanged.connect(self._on_voice_actor_selected)
        self.input_tts_voice.editTextChanged.connect(lambda _v: self._schedule_tts_auto_apply())
        voice_row.addWidget(self.input_tts_voice)
        layout.addLayout(voice_row)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("Text-to-Speech Runtime"))

        tts_model_row = QHBoxLayout()
        tts_model_row.addWidget(QLabel("Model:"))
        self.input_tts_model = QComboBox()
        self.input_tts_model.setEditable(True)
        self.input_tts_model.addItems(TTS_MODEL_PRESETS)
        self.input_tts_model.setCurrentText(LEMONFOX_TTS_MODEL)
        self.input_tts_model.currentTextChanged.connect(lambda _v: self._schedule_tts_auto_apply())
        tts_model_row.addWidget(self.input_tts_model)
        layout.addLayout(tts_model_row)

        tts_lang_row = QHBoxLayout()
        tts_lang_row.addWidget(QLabel("Language:"))
        self.input_tts_language = QComboBox()
        self.input_tts_language.setEditable(True)
        self.input_tts_language.addItems(TTS_LANGUAGE_PRESETS)
        self.input_tts_language.setCurrentText(LEMONFOX_TTS_LANGUAGE)
        self.input_tts_language.currentTextChanged.connect(lambda _v: self._schedule_tts_auto_apply())
        tts_lang_row.addWidget(self.input_tts_language)
        layout.addLayout(tts_lang_row)

        tts_fmt_row = QHBoxLayout()
        tts_fmt_row.addWidget(QLabel("Response Format:"))
        self.input_tts_response_format = QComboBox()
        self.input_tts_response_format.setEditable(True)
        self.input_tts_response_format.addItems(TTS_RESPONSE_FORMAT_PRESETS)
        self.input_tts_response_format.setCurrentText(LEMONFOX_TTS_RESPONSE_FORMAT)
        self.input_tts_response_format.currentTextChanged.connect(lambda _v: self._schedule_tts_auto_apply())
        tts_fmt_row.addWidget(self.input_tts_response_format)
        layout.addLayout(tts_fmt_row)

        tts_speed_row = QHBoxLayout()
        tts_speed_row.addWidget(QLabel("Speed:"))
        self.input_tts_speed = QDoubleSpinBox()
        self.input_tts_speed.setDecimals(2)
        self.input_tts_speed.setRange(TTS_SPEED_MIN, TTS_SPEED_MAX)
        self.input_tts_speed.setSingleStep(0.05)
        self.input_tts_speed.setValue(self._coerce_tts_speed(LEMONFOX_TTS_SPEED))
        self.input_tts_speed.valueChanged.connect(lambda _v: self._schedule_tts_auto_apply())
        tts_speed_row.addWidget(self.input_tts_speed)
        layout.addLayout(tts_speed_row)

        tts_btn_row = QHBoxLayout()
        self.btn_tts_settings_save = QPushButton("Save TTS Settings")
        self.btn_tts_settings_defaults = QPushButton("Restore TTS Defaults")
        self.btn_tts_settings_save.setIcon(ui_icon(self, "settings_tts_save"))
        self.btn_tts_settings_defaults.setIcon(ui_icon(self, "settings_tts_defaults"))
        self.btn_tts_settings_save.clicked.connect(self._emit_tts_settings)
        self.btn_tts_settings_defaults.clicked.connect(self._restore_default_tts_settings)
        tts_btn_row.addWidget(self.btn_tts_settings_save)
        tts_btn_row.addWidget(self.btn_tts_settings_defaults)
        layout.addLayout(tts_btn_row)

        layout.addWidget(QLabel(""))
        layout.addWidget(QLabel("TTS Quick Profiles"))
        layout.addWidget(QLabel("Selecting a profile applies it immediately to voice filters and TTS runtime settings."))

        tts_profile_row = QHBoxLayout()
        tts_profile_row.addWidget(QLabel("TTS Profile:"))
        self.combo_tts_profiles = QComboBox()
        self.combo_tts_profiles.setEditable(False)
        self.combo_tts_profiles.currentTextChanged.connect(self._on_tts_profile_combo_changed)
        tts_profile_row.addWidget(self.combo_tts_profiles)
        layout.addLayout(tts_profile_row)

        tts_profile_btn_row = QHBoxLayout()
        self.btn_tts_profile_save_new = QPushButton("Save as New")
        self.btn_tts_profile_update = QPushButton("Update Current")
        self.btn_tts_profile_delete = QPushButton("Delete")
        self.btn_tts_profile_save_new.setIcon(ui_icon(self, "settings_profile_save_new"))
        self.btn_tts_profile_update.setIcon(ui_icon(self, "settings_profile_update"))
        self.btn_tts_profile_delete.setIcon(ui_icon(self, "settings_profile_delete"))
        self.btn_tts_profile_save_new.clicked.connect(self._save_tts_profile_as_new)
        self.btn_tts_profile_update.clicked.connect(self._update_selected_tts_profile)
        self.btn_tts_profile_delete.clicked.connect(self._delete_selected_tts_profile)
        tts_profile_btn_row.addWidget(self.btn_tts_profile_save_new)
        tts_profile_btn_row.addWidget(self.btn_tts_profile_update)
        tts_profile_btn_row.addWidget(self.btn_tts_profile_delete)
        layout.addLayout(tts_profile_btn_row)

        self._refresh_voice_actor_options()
        layout.addStretch()
        return page

    # ── Hotkey actions ─────────────────────────────────────────────

    def _save_hotkeys(self):
        if not self.hotkeys:
            return
        listen_hotkey = self.input_listen_hotkey.text().strip()
        record_hotkey = self.input_record_hotkey.text().strip()
        try:
            self.hotkeys.update_hotkeys(listen_hotkey, record_hotkey)
            applied_listen, applied_record, _applied_dialogue = self.hotkeys.get_hotkeys()
            self.input_listen_hotkey.setText(applied_listen)
            self.input_record_hotkey.setText(applied_record)
            self.hotkeys_save_requested.emit(applied_listen, applied_record)
        except Exception as e:
            QMessageBox.warning(self, "Hotkey Error", str(e))

    def _restore_default_hotkeys(self):
        self.input_listen_hotkey.setText(DEFAULT_HOTKEY_LISTEN)
        self.input_record_hotkey.setText(DEFAULT_HOTKEY_RECORD)
        self._save_hotkeys()

    def _emit_ui_settings(self):
        self.ui_settings_changed.emit({"dark_mode": bool(self.chk_dark_mode.isChecked())})

    # ── STT / VAD helpers ──────────────────────────────────────────

    @staticmethod
    def _clamp_noise(value) -> int:
        try:
            level = int(value)
        except (TypeError, ValueError):
            level = VAD_NOISE_DEFAULT
        return max(VAD_NOISE_MIN, min(VAD_NOISE_MAX, level))

    @staticmethod
    def _clamp_aggressiveness(value) -> int:
        try:
            level = int(value)
        except (TypeError, ValueError):
            level = VAD_AGGRESSIVENESS
        return max(0, min(3, level))

    @staticmethod
    def _clamp_min_speech(value) -> float:
        try:
            seconds = float(value)
        except (TypeError, ValueError):
            seconds = VAD_MIN_SPEECH_SECONDS
        return max(0.10, min(3.00, round(seconds, 2)))

    @staticmethod
    def _suggest_vad_from_noise(noise_level: int) -> tuple[int, float]:
        level = max(VAD_NOISE_MIN, min(VAD_NOISE_MAX, int(noise_level)))
        aggressiveness = int(round(level / 33.333))
        aggressiveness = max(0, min(3, aggressiveness))
        min_speech = VAD_MIN_SPEECH_FLOOR + ((VAD_MIN_SPEECH_CEIL - VAD_MIN_SPEECH_FLOOR) * (level / 100.0))
        min_speech = round(min_speech, 2)
        return aggressiveness, min_speech

    @staticmethod
    def _estimate_noise_level(vad_aggressiveness, vad_min_speech_seconds) -> int:
        aggr = max(0.0, min(1.0, float(vad_aggressiveness) / 3.0))
        min_ratio = (float(vad_min_speech_seconds) - VAD_MIN_SPEECH_FLOOR) / (
            VAD_MIN_SPEECH_CEIL - VAD_MIN_SPEECH_FLOOR
        )
        min_ratio = max(0.0, min(1.0, min_ratio))
        return int(round(((aggr * 0.7) + (min_ratio * 0.3)) * 100))

    def _on_noise_slider_changed(self, value: int):
        self.lbl_vad_noise_value.setText(str(int(value)))
        if self._updating_vad_controls:
            return
        auto_aggr, auto_min_speech = self._suggest_vad_from_noise(int(value))
        self._updating_vad_controls = True
        self.input_vad_aggressiveness.setValue(auto_aggr)
        self.input_vad_min_speech_seconds.setValue(auto_min_speech)
        self._updating_vad_controls = False
        self._update_vad_summary()
        self._schedule_stt_auto_apply()

    def _on_manual_vad_changed(self, _value):
        if not self._updating_vad_controls:
            self._update_vad_summary()
            self._schedule_stt_auto_apply()

    def _schedule_stt_auto_apply(self):
        self._stt_auto_apply_timer.start(300)

    def _update_vad_summary(self):
        noise = int(self.slider_vad_noise.value())
        auto_aggr, auto_min_speech = self._suggest_vad_from_noise(noise)
        manual_aggr = int(self.input_vad_aggressiveness.value())
        manual_min = float(self.input_vad_min_speech_seconds.value())
        self.lbl_vad_noise_value.setText(str(noise))
        self.lbl_vad_summary.setText(
            f"Auto from noise: agg {auto_aggr}, min {auto_min_speech:.2f}s | "
            f"Manual in use: agg {manual_aggr}, min {manual_min:.2f}s"
        )

    # ── STT settings actions ───────────────────────────────────────

    def _emit_stt_settings(self, show_status=True):
        try:
            settings = self.collect_stt_settings()
            self.stt_settings_changed.emit(settings)
        except Exception as e:
            if show_status:
                QMessageBox.warning(self, "STT Settings Error", str(e))

    def _restore_default_stt_settings(self):
        self._set_combo_value(self.input_stt_language, LEMONFOX_LANGUAGE)
        self._set_combo_value(self.input_stt_response_format, LEMONFOX_RESPONSE_FORMAT)
        self.chk_auto_copy_transcription.setChecked(True)
        self.chk_clear_output_after_copy.setChecked(False)
        self.chk_stop_listening_after_copy.setChecked(False)
        self.chk_keep_wrapping_parentheses.setChecked(False)
        self._updating_vad_controls = True
        self.input_vad_aggressiveness.setValue(self._clamp_aggressiveness(VAD_AGGRESSIVENESS))
        self.input_vad_min_speech_seconds.setValue(self._clamp_min_speech(VAD_MIN_SPEECH_SECONDS))
        self.slider_vad_noise.setValue(self._estimate_noise_level(VAD_AGGRESSIVENESS, VAD_MIN_SPEECH_SECONDS))
        self._updating_vad_controls = False
        self._update_vad_summary()
        self._emit_stt_settings()

    # ── TTS settings actions ───────────────────────────────────────

    def _emit_tts_settings(self, show_status=True, silent=False):
        try:
            self._tts_auto_apply_timer.stop()
            settings = self.collect_tts_settings()
            if silent:
                settings["_silent"] = True
            self.tts_settings_changed.emit(settings)
        except Exception as e:
            if show_status:
                QMessageBox.warning(self, "TTS Settings Error", str(e))

    def _restore_default_tts_settings(self):
        self._updating_tts_controls = True
        self._set_combo_value(self.input_tts_model, LEMONFOX_TTS_MODEL)
        self._set_voice_combo_value(LEMONFOX_TTS_VOICE)
        self._set_combo_value(self.input_tts_language, LEMONFOX_TTS_LANGUAGE)
        self._set_combo_value(self.input_tts_response_format, LEMONFOX_TTS_RESPONSE_FORMAT)
        self.input_tts_speed.setValue(self._coerce_tts_speed(LEMONFOX_TTS_SPEED))
        self._updating_tts_controls = False
        self._emit_tts_settings()

    def _schedule_tts_auto_apply(self):
        if self._updating_tts_controls:
            return
        self._tts_auto_apply_timer.start(300)

    # ── Profile actions ────────────────────────────────────────────

    def _collect_profile_payload(self) -> dict:
        return {
            "stt_language": self.input_stt_language.currentText().strip(),
            "stt_response_format": self.input_stt_response_format.currentText().strip().lower(),
            "vad_noise_level": int(self.slider_vad_noise.value()),
            "vad_aggressiveness": int(self.input_vad_aggressiveness.value()),
            "vad_min_speech_seconds": float(self.input_vad_min_speech_seconds.value()),
            "tts_model": self.input_tts_model.currentText().strip(),
            "tts_voice": self._current_voice_value(),
            "tts_language": self.input_tts_language.currentText().strip(),
            "tts_response_format": self.input_tts_response_format.currentText().strip().lower(),
            "tts_speed": self._format_tts_speed(self.input_tts_speed.value()),
        }

    def _build_profile(self, name: str) -> dict:
        profile = {"name": name.strip()}
        profile.update(self._collect_profile_payload())
        return profile

    def _refresh_profiles_combo(self):
        current = self.combo_profiles.currentText().strip() if hasattr(self, "combo_profiles") else ""
        self.combo_profiles.blockSignals(True)
        self.combo_profiles.clear()
        for profile in self._profiles:
            self.combo_profiles.addItem(profile["name"])
        idx = self.combo_profiles.findText(current)
        self.combo_profiles.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_profiles.blockSignals(False)

    def _emit_profiles_changed(self):
        if self._profiles:
            self.profiles_changed.emit(
                {
                    "profiles": self._profiles,
                    "active_profile": self.combo_profiles.currentText().strip() or self._profiles[0]["name"],
                }
            )

    def _find_profile_by_name(self, name: str):
        for profile in self._profiles:
            if profile["name"] == name:
                return profile
        return None

    def _apply_profile_to_ui(self, profile: dict):
        self._set_combo_value(self.input_stt_language, profile.get("stt_language", LEMONFOX_LANGUAGE))
        self._set_combo_value(
            self.input_stt_response_format,
            profile.get("stt_response_format", LEMONFOX_RESPONSE_FORMAT),
        )
        self._updating_vad_controls = True
        self.slider_vad_noise.setValue(
            self._clamp_noise(
                profile.get(
                    "vad_noise_level",
                    self._estimate_noise_level(
                        profile.get("vad_aggressiveness", VAD_AGGRESSIVENESS),
                        profile.get("vad_min_speech_seconds", VAD_MIN_SPEECH_SECONDS),
                    ),
                )
            )
        )
        self.input_vad_aggressiveness.setValue(
            self._clamp_aggressiveness(profile.get("vad_aggressiveness", VAD_AGGRESSIVENESS))
        )
        self.input_vad_min_speech_seconds.setValue(
            self._clamp_min_speech(profile.get("vad_min_speech_seconds", VAD_MIN_SPEECH_SECONDS))
        )
        self._updating_vad_controls = False
        self._update_vad_summary()
        self._updating_tts_controls = True
        self._set_combo_value(self.input_tts_model, profile.get("tts_model", LEMONFOX_TTS_MODEL))
        self._set_voice_combo_value(profile.get("tts_voice", LEMONFOX_TTS_VOICE))
        self._set_combo_value(self.input_tts_language, profile.get("tts_language", LEMONFOX_TTS_LANGUAGE))
        self._set_combo_value(
            self.input_tts_response_format,
            profile.get("tts_response_format", LEMONFOX_TTS_RESPONSE_FORMAT),
        )
        self.input_tts_speed.setValue(self._coerce_tts_speed(profile.get("tts_speed", LEMONFOX_TTS_SPEED)))
        self._updating_tts_controls = False
        self._emit_stt_settings(show_status=False)
        self._emit_tts_settings(show_status=False, silent=True)

    def _apply_selected_profile(self):
        name = self.combo_profiles.currentText().strip()
        profile = self._find_profile_by_name(name)
        if not profile:
            return
        self._apply_profile_to_ui(profile)
        self._emit_profiles_changed()

    def _save_profile_as_new(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Profile nickname:")
        name = (name or "").strip()
        if not ok or not name:
            return
        if self._find_profile_by_name(name):
            QMessageBox.warning(self, "Profile Error", "A profile with that name already exists.")
            return
        try:
            self._emit_stt_settings(show_status=False)
            self._emit_tts_settings(show_status=False)
            self._profiles.append(self._build_profile(name))
            self._refresh_profiles_combo()
            self._set_combo_value(self.combo_profiles, name)
            self._emit_profiles_changed()
        except Exception as e:
            QMessageBox.warning(self, "Profile Error", str(e))

    def _update_selected_profile(self):
        name = self.combo_profiles.currentText().strip()
        profile = self._find_profile_by_name(name)
        if not profile:
            return
        try:
            self._emit_stt_settings(show_status=False)
            self._emit_tts_settings(show_status=False)
            updated = self._build_profile(name)
            profile.clear()
            profile.update(updated)
            self._emit_profiles_changed()
        except Exception as e:
            QMessageBox.warning(self, "Profile Error", str(e))

    def _delete_selected_profile(self):
        name = self.combo_profiles.currentText().strip()
        if not name or len(self._profiles) <= 1:
            return
        confirm = QMessageBox.question(
            self, "Delete Profile", f"Delete profile '{name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._profiles = [p for p in self._profiles if p["name"] != name]
        self._refresh_profiles_combo()
        self._emit_profiles_changed()

    # ── TTS profile actions ────────────────────────────────────────

    def _collect_tts_profile_payload(self) -> dict:
        payload = self.collect_tts_settings()
        payload["voice_filter_language"] = (
            self.combo_voice_filter_language.currentText().strip().lower() or "any"
        )
        payload["voice_filter_gender"] = (
            self.combo_voice_filter_gender.currentText().strip().lower() or "any"
        )
        return payload

    def _build_tts_profile(self, name: str) -> dict:
        profile = {"name": name.strip()}
        profile.update(self._collect_tts_profile_payload())
        return profile

    def _refresh_tts_profiles_combo(self):
        current = self.combo_tts_profiles.currentText().strip() if hasattr(self, "combo_tts_profiles") else ""
        self.combo_tts_profiles.blockSignals(True)
        self.combo_tts_profiles.clear()
        for profile in self._tts_profiles:
            self.combo_tts_profiles.addItem(profile["name"])
        idx = self.combo_tts_profiles.findText(current)
        self.combo_tts_profiles.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_tts_profiles.blockSignals(False)

    def _emit_tts_profiles_changed(self):
        if self._tts_profiles:
            self.tts_profiles_changed.emit(
                {
                    "tts_profiles": self._tts_profiles,
                    "active_tts_profile": self.combo_tts_profiles.currentText().strip() or self._tts_profiles[0]["name"],
                }
            )

    def _find_tts_profile_by_name(self, name: str):
        for profile in self._tts_profiles:
            if profile["name"] == name:
                return profile
        return None

    def _apply_tts_profile_to_ui(self, profile: dict, emit_tts: bool = True):
        self._updating_tts_controls = True
        self._set_combo_value(self.combo_voice_filter_language, profile.get("voice_filter_language", "any"))
        self._set_combo_value(self.combo_voice_filter_gender, profile.get("voice_filter_gender", "any"))
        self._refresh_voice_actor_options()
        self._set_combo_value(self.input_tts_model, profile.get("tts_model", LEMONFOX_TTS_MODEL))
        self._set_voice_combo_value(profile.get("tts_voice", LEMONFOX_TTS_VOICE))
        self._set_combo_value(self.input_tts_language, profile.get("tts_language", LEMONFOX_TTS_LANGUAGE))
        self._set_combo_value(
            self.input_tts_response_format,
            profile.get("tts_response_format", LEMONFOX_TTS_RESPONSE_FORMAT),
        )
        self.input_tts_speed.setValue(self._coerce_tts_speed(profile.get("tts_speed", LEMONFOX_TTS_SPEED)))
        self._updating_tts_controls = False
        if emit_tts:
            self._emit_tts_settings(show_status=False, silent=True)

    def _apply_selected_tts_profile(self):
        name = self.combo_tts_profiles.currentText().strip()
        profile = self._find_tts_profile_by_name(name)
        if not profile:
            return
        self._apply_tts_profile_to_ui(profile, emit_tts=True)
        self._emit_tts_profiles_changed()

    def _on_tts_profile_combo_changed(self, _name: str):
        self._apply_selected_tts_profile()

    def _save_tts_profile_as_new(self):
        name, ok = QInputDialog.getText(self, "Save TTS Profile", "TTS profile nickname:")
        name = (name or "").strip()
        if not ok or not name:
            return
        if self._find_tts_profile_by_name(name):
            QMessageBox.warning(self, "TTS Profile Error", "A TTS profile with that name already exists.")
            return
        try:
            self._emit_tts_settings(show_status=False, silent=True)
            self._tts_profiles.append(self._build_tts_profile(name))
            self._refresh_tts_profiles_combo()
            self._set_combo_value(self.combo_tts_profiles, name)
        except Exception as e:
            QMessageBox.warning(self, "TTS Profile Error", str(e))

    def _update_selected_tts_profile(self):
        name = self.combo_tts_profiles.currentText().strip()
        profile = self._find_tts_profile_by_name(name)
        if not profile:
            return
        try:
            self._emit_tts_settings(show_status=False, silent=True)
            updated = self._build_tts_profile(name)
            profile.clear()
            profile.update(updated)
            self._emit_tts_profiles_changed()
        except Exception as e:
            QMessageBox.warning(self, "TTS Profile Error", str(e))

    def _delete_selected_tts_profile(self):
        name = self.combo_tts_profiles.currentText().strip()
        if not name or len(self._tts_profiles) <= 1:
            return
        confirm = QMessageBox.question(
            self, "Delete TTS Profile", f"Delete TTS profile '{name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._tts_profiles = [p for p in self._tts_profiles if p["name"] != name]
        self._refresh_tts_profiles_combo()
        self._emit_tts_profiles_changed()

    # ── Voice preset helpers ───────────────────────────────────────

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str):
        combo.setCurrentText(str(value or ""))

    @staticmethod
    def _format_tts_speed(value: float) -> str:
        text = f"{float(value):.2f}".rstrip("0").rstrip(".")
        return text if "." in text else f"{text}.0"

    @staticmethod
    def _coerce_tts_speed(value) -> float:
        if isinstance(value, (int, float)):
            speed = float(value)
        else:
            raw = str(value or "").strip().replace(",", ".")
            try:
                speed = float(raw)
            except (TypeError, ValueError):
                speed = float(LEMONFOX_TTS_SPEED)
        if speed <= 0:
            speed = float(LEMONFOX_TTS_SPEED)
        return max(TTS_SPEED_MIN, min(TTS_SPEED_MAX, speed))

    def _current_voice_value(self) -> str:
        typed = self.input_tts_voice.currentText().strip()
        idx = self.input_tts_voice.currentIndex()
        if idx >= 0:
            data = self.input_tts_voice.itemData(idx)
            label = self.input_tts_voice.itemText(idx).strip()
            if isinstance(data, str) and data.strip() and (not typed or typed == label):
                return data.strip()
        if typed:
            return typed
        return ""

    def _set_voice_combo_value(self, voice_id: str):
        voice_id = (voice_id or "").strip()
        for i in range(self.input_tts_voice.count()):
            data = self.input_tts_voice.itemData(i)
            label = self.input_tts_voice.itemText(i).strip()
            if isinstance(data, str) and data.lower() == voice_id.lower():
                self.input_tts_voice.setCurrentIndex(i)
                return
            if label and label.lower() == voice_id.lower():
                self.input_tts_voice.setCurrentIndex(i)
                return
        self.input_tts_voice.setEditText(voice_id)

    def _refresh_voice_actor_options(self):
        if not hasattr(self, "input_tts_voice"):
            return
        selected_voice = self._current_voice_value() if self.input_tts_voice.count() else self.input_tts_voice.currentText().strip()
        lang_filter = self.combo_voice_filter_language.currentText().strip().lower() if hasattr(self, "combo_voice_filter_language") else "any"
        gender_filter = self.combo_voice_filter_gender.currentText().strip().lower() if hasattr(self, "combo_voice_filter_gender") else "any"

        voices = []
        for v in self._voice_presets:
            v_lang = str(v.get("language", "")).lower()
            v_gender = str(v.get("gender", "")).lower()
            if lang_filter != "any" and v_lang != lang_filter:
                continue
            if gender_filter != "any" and v_gender != gender_filter:
                continue
            voices.append(v)

        self.input_tts_voice.blockSignals(True)
        self.input_tts_voice.clear()
        for v in voices:
            actor = v.get("actor", v.get("id", "voice"))
            label = f"{actor} ({v.get('language', 'n/a')}, {v.get('gender', 'n/a')})"
            self.input_tts_voice.addItem(label, v.get("id", ""))
        self.input_tts_voice.blockSignals(False)

        if selected_voice:
            self._set_voice_combo_value(selected_voice)
        elif self.input_tts_voice.count() > 0:
            self.input_tts_voice.setCurrentIndex(0)

    def _on_voice_actor_selected(self, _index):
        idx = self.input_tts_voice.currentIndex()
        if idx >= 0:
            data = self.input_tts_voice.itemData(idx)
            if isinstance(data, str) and data.strip():
                self.input_tts_voice.setEditText(data.strip())
        self._schedule_tts_auto_apply()

    def _voice_languages(self):
        langs = sorted(
            {
                str(v.get("language", "")).strip().lower()
                for v in self._voice_presets
                if isinstance(v, dict) and str(v.get("language", "")).strip()
            }
        )
        return langs or list(TTS_LANGUAGE_PRESETS)

    @staticmethod
    def _load_voice_presets():
        fallback = [
            {"id": "heart", "actor": "Heart", "language": "en-us", "gender": "female"},
            {"id": "alloy", "actor": "Alloy", "language": "en-us", "gender": "male"},
            {"id": "shimmer", "actor": "Shimmer", "language": "en-us", "gender": "female"},
            {"id": "echo", "actor": "Echo", "language": "en-us", "gender": "male"},
        ]
        try:
            raw = json.loads(VOICE_PRESETS_PATH.read_text(encoding="utf-8"))
            voices = raw.get("voices", []) if isinstance(raw, dict) else []
            cleaned = []
            for v in voices:
                if not isinstance(v, dict):
                    continue
                voice_id = str(v.get("id", "")).strip()
                actor = str(v.get("actor", voice_id)).strip()
                language = str(v.get("language", "")).strip().lower()
                gender = str(v.get("gender", "")).strip().lower()
                if not voice_id or not language:
                    continue
                if gender not in {"male", "female", "neutral"}:
                    gender = "neutral"
                cleaned.append({"id": voice_id, "actor": actor or voice_id, "language": language, "gender": gender})
            return cleaned or fallback
        except (json.JSONDecodeError, OSError):
            return fallback
