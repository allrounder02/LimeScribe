"""Tests for LemonFoxChatClient.complete_stream() SSE parsing."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from core.lemonfox_chat_client import LemonFoxChatClient


def _make_sse_lines(deltas: list[str], include_done: bool = True) -> list[str]:
    """Build SSE lines that iter_lines() would yield."""
    lines = []
    for i, text in enumerate(deltas):
        chunk = {
            "choices": [{"delta": {"content": text}, "index": 0}],
        }
        lines.append(f"data: {json.dumps(chunk)}")
    if include_done:
        lines.append("data: [DONE]")
    return lines


def _mock_stream_response(lines: list[str], status_code: int = 200):
    """Create a mock context-manager response for client.stream()."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    resp.iter_lines = MagicMock(return_value=iter(lines))
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=resp)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


class TestCompleteStream:
    def _client(self):
        return LemonFoxChatClient(
            api_key="test-key",
            chat_url="https://example.com/v1/chat/completions",
            fallback_url="",
            model="test-model",
        )

    def test_yields_content_deltas(self):
        client = self._client()
        lines = _make_sse_lines(["Hello", " world", "!"])
        mock_resp = _mock_stream_response(lines)

        with patch("core.lemonfox_chat_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.stream = MagicMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = list(client.complete_stream([{"role": "user", "content": "hi"}]))

        assert result == ["Hello", " world", "!"]

    def test_handles_done_sentinel(self):
        client = self._client()
        lines = [
            f'data: {json.dumps({"choices": [{"delta": {"content": "A"}}]})}',
            "data: [DONE]",
            f'data: {json.dumps({"choices": [{"delta": {"content": "B"}}]})}',
        ]
        mock_resp = _mock_stream_response(lines, status_code=200)
        # Re-mock to use our custom lines directly
        resp_obj = mock_resp.__enter__()
        resp_obj.iter_lines.return_value = iter(lines)

        with patch("core.lemonfox_chat_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.stream = MagicMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = list(client.complete_stream([{"role": "user", "content": "hi"}]))

        assert result == ["A"]

    def test_skips_empty_content(self):
        client = self._client()
        lines = [
            f'data: {json.dumps({"choices": [{"delta": {"role": "assistant"}}]})}',
            f'data: {json.dumps({"choices": [{"delta": {"content": ""}}]})}',
            f'data: {json.dumps({"choices": [{"delta": {"content": "Hi"}}]})}',
            "data: [DONE]",
        ]
        mock_resp = _mock_stream_response(lines)
        resp_obj = mock_resp.__enter__()
        resp_obj.iter_lines.return_value = iter(lines)

        with patch("core.lemonfox_chat_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.stream = MagicMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = list(client.complete_stream([{"role": "user", "content": "hi"}]))

        assert result == ["Hi"]

    def test_skips_non_data_lines(self):
        client = self._client()
        lines = [
            ": keep-alive",
            "",
            f'data: {json.dumps({"choices": [{"delta": {"content": "Ok"}}]})}',
            "data: [DONE]",
        ]
        mock_resp = _mock_stream_response(lines)
        resp_obj = mock_resp.__enter__()
        resp_obj.iter_lines.return_value = iter(lines)

        with patch("core.lemonfox_chat_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.stream = MagicMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = list(client.complete_stream([{"role": "user", "content": "hi"}]))

        assert result == ["Ok"]

    def test_rejects_empty_messages(self):
        client = self._client()
        with pytest.raises(ValueError, match="non-empty list"):
            list(client.complete_stream([]))

    def test_rejects_empty_model(self):
        client = self._client()
        # Override model to empty after construction
        client.model = ""
        with pytest.raises(ValueError, match="model cannot be empty"):
            list(client.complete_stream([{"role": "user", "content": "hi"}]))
