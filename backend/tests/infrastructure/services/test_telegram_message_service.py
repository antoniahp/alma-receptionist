import pytest

from domain.exceptions import MessageNotSent
from infrastructure.services import telegram_message_service
from infrastructure.services.telegram_message_service import TelegramMessageService


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


@pytest.fixture
def requests_sent(monkeypatch):
    """Guarda cada petición a Telegram en vez de enviarla."""
    sent = []

    def fake_post(url, json, timeout):
        sent.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse({"ok": True, "result": []})

    monkeypatch.setattr(telegram_message_service.requests, "post", fake_post)
    return sent


def test_get_updates_sends_the_long_poll_timeout_to_telegram(requests_sent):
    TelegramMessageService(token="abc").get_updates(offset=7, timeout=25)

    assert requests_sent[0]["url"].endswith("/getUpdates")
    assert requests_sent[0]["json"]["timeout"] == 25
    assert requests_sent[0]["json"]["offset"] == 7
    assert requests_sent[0]["timeout"] == 35


def test_send_typing_uses_a_short_request_timeout(requests_sent):
    TelegramMessageService(token="abc").send_typing("555")

    assert requests_sent[0]["json"] == {"chat_id": "555", "action": "typing"}
    assert requests_sent[0]["timeout"] == 5


def test_without_token_nothing_is_sent(requests_sent):
    with pytest.raises(MessageNotSent):
        TelegramMessageService(token="").get_updates()

    assert requests_sent == []
