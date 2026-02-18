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
