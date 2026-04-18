import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.telegram_service import send_telegram_message, send_alert_match


class TelegramServiceTest(unittest.TestCase):
    def test_send_telegram_message_returns_false_without_bot_token(self):
        with patch("services.telegram_service.os.getenv", return_value=""):
            self.assertFalse(send_telegram_message("Hello", chat_id="123"))

    def test_send_telegram_message_returns_false_without_chat_id(self):
        with patch("services.telegram_service.os.getenv", side_effect=["token", ""]):
            self.assertFalse(send_telegram_message("Hello"))

    def test_send_alert_match_uses_send_telegram_message(self):
        match = {"name": "Test Deal", "url": "https://example.com/item/1"}
        with patch("services.telegram_service.send_telegram_message", return_value=True) as mocked_send:
            result = send_alert_match(match, "12345")

        self.assertTrue(result)
        mocked_send.assert_called_once()
        sent_text = mocked_send.call_args[0][0]
        self.assertIn("Test Deal", sent_text)
        self.assertIn("https://example.com/item/1", sent_text)

    def test_send_telegram_message_encodes_reply_markup(self):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"ok": True}).encode("utf-8")
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_response
        mock_context.__exit__.return_value = None

        with patch("services.telegram_service.request.urlopen", return_value=mock_context) as mocked_urlopen:
            sent = send_telegram_message(
                "Test",
                chat_id="12345",
                reply_markup={"inline_keyboard": [[{"text": "OK", "callback_data": "ok"}]]},
            )

        self.assertTrue(sent)
        self.assertTrue(mocked_urlopen.called)


if __name__ == "__main__":
    unittest.main()
