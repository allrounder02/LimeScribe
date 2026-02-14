"""Settings panel widget — General, Speech, Voice sub-tabs + profiles."""

import json
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox,
    QScrollArea, QStyle, QMessageBox, QInputDialog,
)
from PyQt6.QtCore import pyqtSignal

from hotkeys import DEFAULT_HOTKEY_LISTEN, DEFAULT_HOTKEY_RECORD
from config import (
    LEMONFOX_LANGUAGE,
    LEMONFOX_RESPONSE_FORMAT,
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


class SettingsPanel(QWidget):
    """Settings panel with General, Speech, and Voice sub-tabs."""

    hotkeys_save_requested = pyqtSignal(str, str)  # listen_hotkey, record_hotkey
    stt_settings_changed = pyqtSignal(dict)
    tts_settings_changed = pyqtSignal(dict)
    profiles_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._voice_presets = self._load_voice_presets()
        self._profiles = []
        self.hotkeys = None

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

    def apply_stt_settings(self, language: str, response_format: str, auto_copy: bool):
        self._set_combo_value(self.input_stt_language, language)
        self._set_combo_value(self.input_stt_response_format, response_format)
        self.chk_auto_copy_transcription.setChecked(auto_copy)
        self._emit_stt_settings(show_status=False)

    def apply_tts_settings(self, model: str, voice: str, language: str, response_format: str, speed: str):
        self._set_combo_value(self.input_tts_model, model)
        self._set_voice_combo_value(voice)
        self._set_combo_value(self.input_tts_language, language)
        self._set_combo_value(self.input_tts_response_format, response_format)
        self.input_tts_speed.setText(speed)
        self._emit_tts_settings(show_status=False)

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

    # ── Collect settings from UI ───────────────────────────────────

    def collect_stt_settings(self) -> dict:
        language = self.input_stt_language.currentText().strip()
        response_format = self.input_stt_response_format.currentText().strip().lower()
        if not language or not response_format:
            raise ValueError("STT language and response format are required.")
        return {
            "stt_language": language,
            "stt_response_format": response_format,
            "auto_copy_transcription": self.chk_auto_copy_transcription.isChecked(),
        }

    def collect_tts_settings(self) -> dict:
        model = self.input_tts_model.currentText().strip()
        voice = self._current_voice_value()
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

    # ── Page builders ──────────────────────────────────────────────

    @staticmethod
    def _wrap_in_scroll(widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
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
        self.btn_hotkeys_save.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_hotkeys_defaults.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_hotkeys_save.clicked.connect(self._save_hotkeys)
        self.btn_hotkeys_defaults.clicked.connect(self._restore_default_hotkeys)
        btn_row.addWidget(self.btn_hotkeys_save)
        btn_row.addWidget(self.btn_hotkeys_defaults)
        layout.addLayout(btn_row)
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
        stt_lang_row.addWidget(self.input_stt_language)
        layout.addLayout(stt_lang_row)

        stt_fmt_row = QHBoxLayout()
        stt_fmt_row.addWidget(QLabel("Response Format:"))
        self.input_stt_response_format = QComboBox()
        self.input_stt_response_format.setEditable(True)
        self.input_stt_response_format.addItems(STT_RESPONSE_FORMAT_PRESETS)
        self.input_stt_response_format.setCurrentText(LEMONFOX_RESPONSE_FORMAT)
        stt_fmt_row.addWidget(self.input_stt_response_format)
        layout.addLayout(stt_fmt_row)

        stt_btn_row = QHBoxLayout()
        self.btn_stt_settings_save = QPushButton("Save STT Settings")
        self.btn_stt_settings_defaults = QPushButton("Restore STT Defaults")
        self.btn_stt_settings_save.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_stt_settings_defaults.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_stt_settings_save.clicked.connect(self._emit_stt_settings)
        self.btn_stt_settings_defaults.clicked.connect(self._restore_default_stt_settings)
        stt_btn_row.addWidget(self.btn_stt_settings_save)
        stt_btn_row.addWidget(self.btn_stt_settings_defaults)
        layout.addLayout(stt_btn_row)

        self.chk_auto_copy_transcription = QCheckBox("Auto-copy transcription to clipboard")
        self.chk_auto_copy_transcription.setChecked(True)
        layout.addWidget(self.chk_auto_copy_transcription)

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
        self.btn_profile_apply.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.btn_profile_save_new.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.btn_profile_update.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_profile_delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
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
        tts_model_row.addWidget(self.input_tts_model)
        layout.addLayout(tts_model_row)

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
        self.btn_tts_settings_save.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_tts_settings_defaults.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.btn_tts_settings_save.clicked.connect(self._emit_tts_settings)
        self.btn_tts_settings_defaults.clicked.connect(self._restore_default_tts_settings)
        tts_btn_row.addWidget(self.btn_tts_settings_save)
        tts_btn_row.addWidget(self.btn_tts_settings_defaults)
        layout.addLayout(tts_btn_row)

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
            applied_listen, applied_record = self.hotkeys.get_hotkeys()
            self.input_listen_hotkey.setText(applied_listen)
            self.input_record_hotkey.setText(applied_record)
            self.hotkeys_save_requested.emit(applied_listen, applied_record)
        except Exception as e:
            QMessageBox.warning(self, "Hotkey Error", str(e))

    def _restore_default_hotkeys(self):
        self.input_listen_hotkey.setText(DEFAULT_HOTKEY_LISTEN)
        self.input_record_hotkey.setText(DEFAULT_HOTKEY_RECORD)
        self._save_hotkeys()

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
        self._emit_stt_settings()

    # ── TTS settings actions ───────────────────────────────────────

    def _emit_tts_settings(self, show_status=True):
        try:
            settings = self.collect_tts_settings()
            self.tts_settings_changed.emit(settings)
        except Exception as e:
            if show_status:
                QMessageBox.warning(self, "TTS Settings Error", str(e))

    def _restore_default_tts_settings(self):
        self._set_combo_value(self.input_tts_model, LEMONFOX_TTS_MODEL)
        self._set_voice_combo_value(LEMONFOX_TTS_VOICE)
        self._set_combo_value(self.input_tts_language, LEMONFOX_TTS_LANGUAGE)
        self._set_combo_value(self.input_tts_response_format, LEMONFOX_TTS_RESPONSE_FORMAT)
        self.input_tts_speed.setText(str(LEMONFOX_TTS_SPEED))
        self._emit_tts_settings()

    # ── Profile actions ────────────────────────────────────────────

    def _collect_profile_payload(self) -> dict:
        return {
            "stt_language": self.input_stt_language.currentText().strip(),
            "stt_response_format": self.input_stt_response_format.currentText().strip().lower(),
            "tts_model": self.input_tts_model.currentText().strip(),
            "tts_voice": self._current_voice_value(),
            "tts_language": self.input_tts_language.currentText().strip(),
            "tts_response_format": self.input_tts_response_format.currentText().strip().lower(),
            "tts_speed": self.input_tts_speed.text().strip(),
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
        self._set_combo_value(self.input_tts_model, profile.get("tts_model", LEMONFOX_TTS_MODEL))
        self._set_voice_combo_value(profile.get("tts_voice", LEMONFOX_TTS_VOICE))
        self._set_combo_value(self.input_tts_language, profile.get("tts_language", LEMONFOX_TTS_LANGUAGE))
        self._set_combo_value(
            self.input_tts_response_format,
            profile.get("tts_response_format", LEMONFOX_TTS_RESPONSE_FORMAT),
        )
        self.input_tts_speed.setText(str(profile.get("tts_speed", LEMONFOX_TTS_SPEED)))
        self._emit_stt_settings(show_status=False)
        self._emit_tts_settings(show_status=False)

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

    # ── Voice preset helpers ───────────────────────────────────────

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str):
        combo.setCurrentText(str(value or ""))

    def _current_voice_value(self) -> str:
        idx = self.input_tts_voice.currentIndex()
        if idx >= 0:
            data = self.input_tts_voice.itemData(idx)
            if isinstance(data, str) and data.strip():
                return data.strip()
        return self.input_tts_voice.currentText().strip()

    def _set_voice_combo_value(self, voice_id: str):
        voice_id = (voice_id or "").strip()
        for i in range(self.input_tts_voice.count()):
            data = self.input_tts_voice.itemData(i)
            if isinstance(data, str) and data == voice_id:
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
