"""Unit tests for LemonFoxChatClient response parsing."""

import unittest

from core.lemonfox_chat_client import LemonFoxChatClient


class LemonFoxChatClientParsingTests(unittest.TestCase):
    def test_extract_assistant_content_from_standard_payload(self):
        payload = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello from Llama.",
                    }
                }
            ]
        }
        self.assertEqual(LemonFoxChatClient._extract_assistant_content(payload), "Hello from Llama.")

    def test_extract_assistant_content_raises_when_missing_choices(self):
        with self.assertRaises(RuntimeError):
            LemonFoxChatClient._extract_assistant_content({})

    def test_extract_assistant_content_supports_structured_content_list(self):
        payload = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "output_text", "text": "Line one"},
                            {"type": "output_text", "text": "Line two"},
                        ]
                    }
                }
            ]
        }
        self.assertEqual(LemonFoxChatClient._extract_assistant_content(payload), "Line one\nLine two")


if __name__ == "__main__":
    unittest.main()
