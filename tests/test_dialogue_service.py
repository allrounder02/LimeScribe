"""Unit tests for DialogueService history behavior."""

import threading
import unittest

from core.app_config import AppConfig
from core.dialogue_service import DialogueService


class _FakeChatClient:
    def __init__(self):
        self.calls: list[list[dict]] = []
        self.model = "llama-8b-chat"

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        self.calls.append([dict(m) for m in messages])
        return "assistant-reply"


class DialogueServiceTests(unittest.TestCase):
    def _run_send(self, service: DialogueService, message: str) -> dict:
        done = threading.Event()
        result: dict = {}

        def on_reply(text: str):
            result["reply"] = text
            done.set()

        def on_error(err: str):
            result["error"] = err
            done.set()

        service._on_reply = on_reply
        service._on_error = on_error
        service.send(message)
        self.assertTrue(done.wait(2.0), "Timed out waiting for dialogue background worker.")
        return result

    def test_include_history_true_reuses_prior_messages(self):
        service = DialogueService(AppConfig(chat_system_prompt="You are helpful."))
        fake_client = _FakeChatClient()
        service.client = fake_client

        first = self._run_send(service, "Hello there")
        second = self._run_send(service, "What did I just ask?")

        self.assertEqual(first.get("reply"), "assistant-reply")
        self.assertEqual(second.get("reply"), "assistant-reply")
        self.assertEqual(len(fake_client.calls), 2)
        self.assertEqual([m["role"] for m in fake_client.calls[0]], ["system", "user"])
        self.assertEqual(
            [m["role"] for m in fake_client.calls[1]],
            ["system", "user", "assistant", "user"],
        )

    def test_include_history_false_sends_only_current_user_message(self):
        service = DialogueService(AppConfig(chat_system_prompt="You are helpful."))
        fake_client = _FakeChatClient()
        service.client = fake_client
        service.update_settings(include_history=False, reset_history=True)

        self._run_send(service, "First")
        self._run_send(service, "Second")

        self.assertEqual(len(fake_client.calls), 2)
        self.assertEqual([m["role"] for m in fake_client.calls[0]], ["system", "user"])
        self.assertEqual([m["role"] for m in fake_client.calls[1]], ["system", "user"])
        self.assertEqual(fake_client.calls[1][-1]["content"], "Second")


if __name__ == "__main__":
    unittest.main()
