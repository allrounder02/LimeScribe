"""Dialogue tab widget for OpenAI-compatible chat conversations."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.icon_library import ui_icon


class DialoguePanel(QWidget):
    """Chat UI controls + conversation transcript view."""

    send_requested = pyqtSignal(str)
    reset_requested = pyqtSignal()
    use_output_requested = pyqtSignal()
    model_changed = pyqtSignal(str)
    system_prompt_changed = pyqtSignal(str)
    history_mode_changed = pyqtSignal(bool)
    voice_start_requested = pyqtSignal()
    voice_stop_requested = pyqtSignal()
    auto_listen_changed = pyqtSignal(bool)
    voice_word_limits_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model"))
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True)
        self.combo_model.addItems(["llama-8b-chat", "llama-70b-chat"])
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        model_row.addWidget(self.combo_model)
        layout.addLayout(model_row)

        prompt_row = QHBoxLayout()
        prompt_row.addWidget(QLabel("System Prompt"))
        self.input_system_prompt = QLineEdit("You are a helpful assistant.")
        self.input_system_prompt.setPlaceholderText("Optional system prompt")
        self.input_system_prompt.editingFinished.connect(self._on_system_prompt_changed)
        prompt_row.addWidget(self.input_system_prompt)
        layout.addLayout(prompt_row)

        options_row = QHBoxLayout()
        self.chk_include_history = QCheckBox("Include conversation history")
        self.chk_include_history.setChecked(True)
        self.chk_include_history.toggled.connect(self.history_mode_changed.emit)
        options_row.addWidget(self.chk_include_history)
        options_row.addStretch()
        layout.addLayout(options_row)

        layout.addWidget(QLabel("Dialogue"))
        self.text_dialogue = QTextEdit()
        self.text_dialogue.setReadOnly(True)
        self.text_dialogue.setPlaceholderText("Conversation will appear here.")
        layout.addWidget(self.text_dialogue)

        # Voice dialogue controls
        voice_row = QHBoxLayout()
        self.btn_voice_toggle = QPushButton("Talk")
        self.btn_voice_toggle.setIcon(ui_icon(self, "tab_listening"))
        self.btn_voice_toggle.setCheckable(True)
        self.btn_voice_toggle.clicked.connect(self._on_voice_toggled)
        voice_row.addWidget(self.btn_voice_toggle)

        self.chk_auto_listen = QCheckBox("Auto-listen")
        self.chk_auto_listen.setChecked(True)
        self.chk_auto_listen.setToolTip("Automatically listen for the next turn after the assistant speaks")
        self.chk_auto_listen.toggled.connect(self.auto_listen_changed.emit)
        voice_row.addWidget(self.chk_auto_listen)

        self.lbl_voice_state = QLabel("")
        voice_row.addWidget(self.lbl_voice_state)
        voice_row.addStretch()
        layout.addLayout(voice_row)

        word_limit_row = QHBoxLayout()
        word_limit_row.addWidget(QLabel("Max words (Auto)"))
        self.spin_voice_max_words_auto = QSpinBox()
        self.spin_voice_max_words_auto.setRange(10, 500)
        self.spin_voice_max_words_auto.setValue(100)
        self.spin_voice_max_words_auto.valueChanged.connect(self._emit_word_limits_changed)
        word_limit_row.addWidget(self.spin_voice_max_words_auto)
        word_limit_row.addSpacing(14)
        word_limit_row.addWidget(QLabel("Max words (Manual)"))
        self.spin_voice_max_words_manual = QSpinBox()
        self.spin_voice_max_words_manual.setRange(10, 500)
        self.spin_voice_max_words_manual.setValue(50)
        self.spin_voice_max_words_manual.valueChanged.connect(self._emit_word_limits_changed)
        word_limit_row.addWidget(self.spin_voice_max_words_manual)
        word_limit_row.addStretch()
        layout.addLayout(word_limit_row)

        layout.addWidget(QLabel("Your Message"))
        self.input_message = QTextEdit()
        self.input_message.setPlaceholderText("Type your message and click Send.")
        self.input_message.setFixedHeight(110)
        layout.addWidget(self.input_message)

        btn_row = QHBoxLayout()
        self.btn_use_output = QPushButton("Use Transcription Output")
        self.btn_send = QPushButton("Send")
        self.btn_reset = QPushButton("New Dialogue")
        self.btn_use_output.setIcon(ui_icon(self, "tts_use_output"))
        self.btn_send.setIcon(ui_icon(self, "dialogue_send"))
        self.btn_reset.setIcon(ui_icon(self, "dialogue_reset"))
        self.btn_use_output.clicked.connect(self.use_output_requested.emit)
        self.btn_send.clicked.connect(self._emit_send)
        self.btn_reset.clicked.connect(self.reset_requested.emit)
        btn_row.addWidget(self.btn_use_output)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_reset)
        btn_row.addWidget(self.btn_send)
        layout.addLayout(btn_row)

    def _emit_send(self):
        text = self.get_message_text()
        if text:
            self.send_requested.emit(text)
            self.input_message.clear()

    def _on_model_changed(self, text: str):
        candidate = (text or "").strip()
        if candidate:
            self.model_changed.emit(candidate)

    def _on_system_prompt_changed(self):
        self.system_prompt_changed.emit(self.get_system_prompt())

    def get_message_text(self) -> str:
        return self.input_message.toPlainText().strip()

    def get_model(self) -> str:
        return self.combo_model.currentText().strip()

    def get_system_prompt(self) -> str:
        return self.input_system_prompt.text().strip()

    def should_include_history(self) -> bool:
        return bool(self.chk_include_history.isChecked())

    def set_busy(self, busy: bool):
        ready = not bool(busy)
        self.btn_send.setEnabled(ready)
        self.btn_reset.setEnabled(ready)
        self.combo_model.setEnabled(ready)
        self.input_system_prompt.setEnabled(ready)
        self.chk_include_history.setEnabled(ready)

    def set_model(self, model: str, emit: bool = False):
        value = (model or "").strip()
        if not value:
            return
        self.combo_model.blockSignals(True)
        idx = self.combo_model.findText(value)
        if idx < 0:
            self.combo_model.addItem(value)
            idx = self.combo_model.findText(value)
        self.combo_model.setCurrentIndex(idx)
        self.combo_model.blockSignals(False)
        if emit:
            self.model_changed.emit(value)

    def set_system_prompt(self, prompt: str, emit: bool = False):
        self.input_system_prompt.blockSignals(True)
        self.input_system_prompt.setText((prompt or "").strip())
        self.input_system_prompt.blockSignals(False)
        if emit:
            self.system_prompt_changed.emit(self.get_system_prompt())

    def set_include_history(self, enabled: bool, emit: bool = False):
        self.chk_include_history.blockSignals(True)
        self.chk_include_history.setChecked(bool(enabled))
        self.chk_include_history.blockSignals(False)
        if emit:
            self.history_mode_changed.emit(bool(enabled))

    def set_input_text(self, text: str):
        self.input_message.setPlainText((text or "").strip())
        self.input_message.setFocus()

    def clear_dialogue(self):
        self.text_dialogue.clear()

    def append_user(self, text: str):
        self._append_message("You", text)

    def append_assistant(self, text: str):
        self._append_message("Assistant", text)

    def append_error(self, text: str):
        self._append_message("Error", text)

    def _on_voice_toggled(self, checked: bool):
        if checked:
            self.voice_start_requested.emit()
        else:
            self.voice_stop_requested.emit()

    def set_voice_state(self, label: str):
        self.lbl_voice_state.setText(label)

    def set_voice_active(self, active: bool):
        self.btn_voice_toggle.blockSignals(True)
        self.btn_voice_toggle.setChecked(active)
        self.btn_voice_toggle.setText("Stop" if active else "Talk")
        self.btn_voice_toggle.blockSignals(False)
        # Disable text input while voice is active
        self.input_message.setEnabled(not active)
        self.btn_send.setEnabled(not active)

    def set_voice_auto_listen(self, enabled: bool):
        self.chk_auto_listen.blockSignals(True)
        self.chk_auto_listen.setChecked(enabled)
        self.chk_auto_listen.blockSignals(False)

    def set_voice_word_limits(self, auto_words: int, manual_words: int, emit: bool = False):
        auto_val = max(10, min(500, int(auto_words)))
        manual_val = max(10, min(500, int(manual_words)))
        self.spin_voice_max_words_auto.blockSignals(True)
        self.spin_voice_max_words_manual.blockSignals(True)
        self.spin_voice_max_words_auto.setValue(auto_val)
        self.spin_voice_max_words_manual.setValue(manual_val)
        self.spin_voice_max_words_auto.blockSignals(False)
        self.spin_voice_max_words_manual.blockSignals(False)
        if emit:
            self.voice_word_limits_changed.emit(auto_val, manual_val)

    def _emit_word_limits_changed(self, _value: int):
        self.voice_word_limits_changed.emit(
            int(self.spin_voice_max_words_auto.value()),
            int(self.spin_voice_max_words_manual.value()),
        )

    def _append_message(self, role: str, text: str):
        body = (text or "").strip()
        if not body:
            return
        stamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{stamp}] {role}:"
        current = self.text_dialogue.toPlainText().rstrip()
        block = f"{prefix}\n{body}"
        self.text_dialogue.setPlainText(f"{current}\n\n{block}" if current else block)
        cursor = self.text_dialogue.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_dialogue.setTextCursor(cursor)
