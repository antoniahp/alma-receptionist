import pytest

from domain.entities import Appointment, Client, HelpRequest
from infrastructure.telegram_bot.update_handler import TelegramUpdateHandler
from tests.fakes import FakeLanguageModelService, FakeMessageService

pytestmark = pytest.mark.django_db

LAURA_CHAT = {"id": 555, "first_name": "Laura"}


@pytest.fixture
def telegram():
    return FakeMessageService()


@pytest.fixture
def handler(repositories, telegram):
    return TelegramUpdateHandler(repositories, telegram, FakeLanguageModelService())


def text_message(text, chat=LAURA_CHAT, **extra):
    return {"update_id": 1, "message": {"chat": chat, "text": text, **extra}}


def button(data, message_id=9):
    return {
        "update_id": 2,
        "callback_query": {"id": "x", "from": LAURA_CHAT, "message": {"chat": LAURA_CHAT, "message_id": message_id}, "data": data},
    }


def test_start_with_code_links_existing_client(handler, telegram, salon):
    handler.handle(text_message(f"/start {salon.laura.telegram_link_code}"))

    salon.laura.refresh_from_db()
    assert salon.laura.telegram_chat_id == "555"
    assert telegram.sent[0]["text"].startswith("¡Hola, Laura!")


def test_full_booking_by_buttons(handler, telegram, salon):
    handler.handle(text_message("/start"))
    handler.handle(text_message("Me duele la espalda, estoy fatal de estrés"))
    recommend_button = telegram.sent[-1]["buttons"][0][0].data
    handler.handle(button(recommend_button))
    first_slot = telegram.sent[-1]["buttons"][0][0].data
    handler.handle(button(first_slot))

    assert Appointment.objects.filter(source=Appointment.SOURCE_TELEGRAM).count() == 1
    assert telegram.sent[-1]["text"].startswith(("¡Hecho", "¡Listo"))


def test_owner_replies_to_alert(handler, telegram, salon):
    handler.handle(text_message("Hola, ¿hacéis depilación láser?"))
    alert = next(item for item in telegram.sent if item["chat_id"] == "999")
    help_request = HelpRequest.objects.get()
    assert help_request.owner_message_id

    handler.handle(
        text_message(
            "En noviembre empezamos, ¡te aviso!", chat={"id": 999}, reply_to_message={"message_id": int(help_request.owner_message_id)}
        )
    )

    assert alert["text"].startswith("🙋")
    assert telegram.sent[-2] == {"chat_id": "555", "text": "En noviembre empezamos, ¡te aviso!", "buttons": []}
    assert telegram.sent[-1]["text"].startswith("✅ Enviado")


def test_owner_message_without_reply_gets_instructions(handler, telegram, salon):
    handler.handle(text_message("hola", chat={"id": 999}))

    assert "Responder" in telegram.sent[-1]["text"]
    assert not Client.objects.filter(telegram_chat_id="999").exists()


def test_non_text_messages(handler, telegram, salon):
    handler.handle({"update_id": 3, "message": {"chat": LAURA_CHAT, "photo": []}})

    assert "solo leo mensajes de texto" in telegram.sent[-1]["text"]


def test_owner_can_open_a_client_link_to_test_reminders(handler, telegram, salon):
    owner_chat = {"id": 999, "first_name": "Cris"}

    handler.handle(text_message(f"/start {salon.laura.telegram_link_code}", chat=owner_chat))

    salon.laura.refresh_from_db()
    assert salon.laura.telegram_chat_id == "999"
    assert telegram.sent[0]["text"].startswith("¡Hola, Laura!")
