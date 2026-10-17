import pytest
from django.utils import timezone

from domain.rules import customer_messages
from domain.rules.language import use

pytestmark = pytest.mark.django_db


def test_start_button_and_message(api_client, salon):
    started = api_client.post("/api/public/chat/", {"start": True}, format="json").json()
    session = started["session"]
    assert started["buttons"][0][0] == {"label": "📅 Pedir cita", "data": "book"}

    prices = api_client.post("/api/public/chat/", {"session": session, "button": "prices"}, format="json").json()
    assert prices["buttons"] == [[{"label": "Facial", "data": "cat:facial:precios"}]]

    facial = api_client.post("/api/public/chat/", {"session": session, "button": "cat:facial:precios"}, format="json").json()
    assert "Masaje relajante" in facial["text"]
    assert "€" in facial["buttons"][0][0]["label"]

    # Si pide cita, los tratamientos salen sin precio
    booking = api_client.post("/api/public/chat/", {"session": session, "button": "cat:facial"}, format="json").json()
    assert booking["buttons"][0][0] == {"label": salon.massage.name, "data": f"svc:{salon.massage.id}"}

    answer = api_client.post("/api/public/chat/", {"session": session, "message": "¿Qué horario tenéis?"}, format="json").json()
    assert "10:00" in answer["text"]
    assert answer["last_id"]
    assert answer["by_ai"] is False


def test_invalid_session_is_rejected(api_client, salon):
    assert api_client.post("/api/public/chat/", {"session": "no-es-uuid", "message": "hola"}, format="json").status_code == 400


def test_the_receptionist_answers_in_english_when_the_website_is_in_english(api_client, salon):
    salon.massage.name_en = "Relaxing massage"
    salon.massage.save()
    english = {"HTTP_ACCEPT_LANGUAGE": "en"}

    started = api_client.post("/api/public/chat/", {"start": True}, format="json", **english).json()
    session = started["session"]
    assert started["text"].startswith("Hi! I’m Aura")
    assert started["buttons"][0][0] == {"label": "📅 Book", "data": "book"}

    booking = api_client.post("/api/public/chat/", {"session": session, "button": "cat:facial"}, format="json", **english).json()
    assert booking["buttons"][0][0]["label"] == "Relaxing massage"

    hours = api_client.post(
        "/api/public/chat/", {"session": session, "message": "What are your opening hours?"}, format="json", **english
    ).json()
    assert hours["text"].startswith("Open Monday to Saturday")

    off_topic = api_client.post(
        "/api/public/chat/", {"session": session, "message": "what is the square root of 50"}, format="json", **english
    ).json()
    assert "I only handle things" in off_topic["text"] or "beyond me" in off_topic["text"]


def test_owner_alerts_stay_in_spanish_even_if_the_client_writes_in_english():
    with use("en"):
        text = customer_messages.owner_new_booking("la web", "Ann", "Masaje", timezone.now())

    assert text.startswith("📅 Nueva cita por la web")
    assert " a las " in text
