import pytest
from model_bakery import baker

from application.commands.handle_chat_button.command import HandleChatButtonCommand
from application.commands.handle_chat_button.command_dto import HandleChatButtonCommandDTO
from application.commands.handle_chat_message.command import HandleChatMessageCommand
from application.commands.handle_chat_message.command_dto import HandleChatMessageCommandDTO
from application.shared.receptionist_actions import ReceptionistActions
from domain.entities import Appointment, ChatMessage, HelpRequest, Service
from infrastructure.repositories.django_repositories import build_django_repositories
from tests.fakes import FakeLanguageModelService
from tests.helpers import button_data, local_datetime

pytestmark = pytest.mark.django_db


def say(message_service, language_model_service, key, text, client_id=None):
    repositories = build_django_repositories()
    return HandleChatMessageCommand(repositories, message_service, language_model_service).execute(
        HandleChatMessageCommandDTO(conversation_key=key, text=text, client_id=client_id)
    )


def press(message_service, key, data, client_id=None):
    repositories = build_django_repositories()
    return HandleChatButtonCommand(repositories, message_service).execute(
        HandleChatButtonCommandDTO(conversation_key=key, data=data, client_id=client_id)
    )


# ---------- respaldo por reglas (IA apagada) ----------


def test_answers_prices_and_hours(salon, message_service, language_model_service):
    assert "45\u00a0€" in say(message_service, language_model_service, "web:a", "¿Cuánto cuesta el masaje?").text
    assert "10:00" in say(message_service, language_model_service, "web:a", "¿Qué horario tenéis?").text


def test_saves_both_sides_of_the_conversation(salon, message_service, language_model_service):
    say(message_service, language_model_service, "web:a", "Hola")

    assert list(ChatMessage.objects.values_list("role", flat=True)) == ["user", "assistant"]


def test_booking_on_the_web_asks_the_phone_and_then_the_name_of_a_new_client(salon, next_monday, message_service, language_model_service):
    reply = say(message_service, language_model_service, "web:b", "Quiero cita para un masaje el lunes por la tarde")
    slots = [data for data in button_data(reply) if data.startswith("slot:")]
    assert slots
    assert all(int(data[-4:-2]) >= 16 for data in slots)

    reply = press(message_service, "web:b", slots[0])
    assert "móvil" in reply.text

    reply = say(message_service, language_model_service, "web:b", "Es el 677 123 456")
    assert "nombre" in reply.text

    reply = say(message_service, language_model_service, "web:b", "Me llamo Marta Ruiz")
    appointment = Appointment.objects.get(pk=reply.appointment_id)
    assert appointment.client.name == "Marta Ruiz"
    assert appointment.client.phone == "677 123 456"
    assert appointment.source == Appointment.SOURCE_WEB


def test_a_returning_client_is_recognised_by_her_phone(salon, next_monday, message_service, language_model_service):
    reply = say(message_service, language_model_service, "web:c", "Quiero cita para un masaje el lunes por la tarde")
    slot = next(data for data in button_data(reply) if data.startswith("slot:"))
    press(message_service, "web:c", slot)

    reply = say(message_service, language_model_service, "web:c", "+34 611 111 111")

    appointment = Appointment.objects.get(pk=reply.appointment_id)
    assert appointment.client == salon.laura
    assert "Laura" in reply.text


def test_without_a_phone_the_booking_waits(salon, next_monday, message_service, language_model_service):
    reply = say(message_service, language_model_service, "web:d", "Quiero cita para un masaje el lunes por la tarde")
    slot = next(data for data in button_data(reply) if data.startswith("slot:"))
    press(message_service, "web:d", slot)

    reply = say(message_service, language_model_service, "web:d", "prefiero no")

    assert "llámanos" in reply.text
    assert not Appointment.objects.filter(source=Appointment.SOURCE_WEB).exists()


def test_follow_up_day_keeps_the_service(salon, next_monday, message_service, language_model_service):
    say(message_service, language_model_service, "web:c", "Quiero un masaje")

    reply = say(message_service, language_model_service, "web:c", "¿Y el lunes por la mañana?")

    assert any(data.startswith(f"slot:{salon.massage.id}:{next_monday:%Y%m%d}") for data in button_data(reply))


def test_is_honest_about_being_virtual(salon, message_service, language_model_service):
    assert "asistente virtual" in say(message_service, language_model_service, "web:d", "¿Eres un bot?").text


def test_unknown_question_goes_to_owner_on_telegram(salon, message_service, language_model_service):
    reply = say(message_service, language_model_service, "tg:77", "¿Hacéis micropigmentación de cejas?", client_id=salon.laura.id)

    assert "Cris" in reply.text
    help_request = HelpRequest.objects.get()
    assert help_request.client == salon.laura
    assert "micropigmentación" in message_service.sent[0]["text"]  # aviso a la dueña (chat 999)


def test_web_handoff_asks_for_optional_phone(salon, message_service, language_model_service):
    reply = say(message_service, language_model_service, "web:e", "¿Hacéis micropigmentación de cejas?")
    assert "teléfono" in reply.text

    reply = say(message_service, language_model_service, "web:e", "Sí, el 612 345 678")

    assert "Gracias" in reply.text
    assert HelpRequest.objects.get().contact == "612 345 678"


# ---------- con IA ----------


def test_ai_books_a_valid_slot_with_its_own_words(salon, next_monday, message_service):
    model = FakeLanguageModelService(
        json_response={
            "reply": "¡Hecho, Laura! Te espero el lunes a las 17:00 😊",
            "action": {"type": "book", "service_id": salon.massage.id, "start": f"{next_monday:%Y-%m-%d} 17:00"},
        }
    )

    reply = say(message_service, model, "tg:1", "El lunes a las 5 para el masaje", client_id=salon.laura.id)

    assert reply.by_ai
    assert reply.text == "¡Hecho, Laura! Te espero el lunes a las 17:00 😊"
    assert Appointment.objects.get(pk=reply.appointment_id).start == local_datetime(next_monday, 17)


def test_ai_booking_on_taken_slot_offers_alternatives(salon, next_monday, message_service):
    Appointment.objects.create(client=salon.laura, service=salon.massage, start=local_datetime(next_monday, 17))
    model = FakeLanguageModelService(
        json_response={
            "reply": "¡Hecho!",
            "action": {"type": "book", "service_id": salon.massage.id, "start": f"{next_monday:%Y-%m-%d} 17:00"},
        }
    )

    reply = say(message_service, model, "tg:2", "El lunes a las 5", client_id=salon.laura.id)

    assert reply.appointment_id is None
    assert any(data.startswith("slot:") for data in button_data(reply))


def test_ai_false_booking_claim_is_corrected(salon, message_service):
    model = FakeLanguageModelService(
        json_response={"reply": "Te he reservado el masaje", "action": {"type": "none", "service_id": salon.massage.id}}
    )

    reply = say(message_service, model, "tg:3", "quiero masaje", client_id=salon.laura.id)

    assert not Appointment.objects.exists()
    assert reply.buttons


def test_ai_mentioning_owner_creates_help_request(salon, message_service):
    model = FakeLanguageModelService(
        json_response={"reply": "Eso no lo sé seguro. Se lo pregunto a Cris y te digo.", "action": {"type": "none"}}
    )

    say(message_service, model, "tg:4", "¿Usáis productos veganos?", client_id=salon.laura.id)

    assert HelpRequest.objects.count() == 1


def test_ai_invalid_json_falls_back_to_rules(salon, message_service):
    model = FakeLanguageModelService(json_response={"nothing": True})

    reply = say(message_service, model, "tg:5", "¿Cuánto cuesta el masaje?", client_id=salon.laura.id)

    assert "45\u00a0€" in reply.text
    assert not reply.by_ai


def test_the_most_specific_service_wins(repositories, salon, message_service):
    facial = baker.make(Service, name="Higiene facial", keywords="facial,limpieza", price=45, duration_minutes=60)
    massage_face = baker.make(Service, name="Masaje facial", keywords="masaje", price=20, duration_minutes=30)
    actions = ReceptionistActions(repositories, message_service)

    assert actions.find_service_in_text("Quiero un masaje facial") == massage_face
    assert actions.find_service_in_text("Me hago una limpieza facial?") == facial


def test_off_topic_questions_get_a_polite_no_and_do_not_bother_the_owner(repositories, salon, message_service):
    language_model = FakeLanguageModelService(json_response={"reply": "√50 ≈ 7,07", "action": {"type": "none"}})

    reply = HandleChatMessageCommand(repositories, message_service, language_model).execute(
        HandleChatMessageCommandDTO(conversation_key="web:raiz", text="dame la raíz cuadrada de 50")
    )

    assert "7,07" not in reply.text
    assert "solo" in reply.text
    assert language_model.received == []  # ni siquiera se le pregunta a la IA
    assert HelpRequest.objects.count() == 0


def test_an_ai_reply_with_code_is_not_sent(repositories, salon, message_service):
    language_model = FakeLanguageModelService(json_response={"reply": "```print('hola')```", "action": {"type": "none"}})

    reply = HandleChatMessageCommand(repositories, message_service, language_model).execute(
        HandleChatMessageCommandDTO(conversation_key="web:codigo", text="¿qué horario tenéis?")
    )

    assert "```" not in reply.text
    assert reply.by_ai is False


def test_a_loose_word_is_not_passed_to_the_owner(salon, message_service, language_model_service):
    reply = say(message_service, language_model_service, "web:p", "playa")

    assert "no te he entendido" in reply.text or "no sé si te sigo" in reply.text
    assert not HelpRequest.objects.exists()


def test_a_real_question_is_passed_once_and_the_next_one_is_added(salon, message_service, language_model_service):
    first = say(message_service, language_model_service, "web:q", "¿Tenéis piscina?")
    second = say(message_service, language_model_service, "web:q", "¿Y aparcamiento cerca?")

    assert "Cris" in first.text
    assert "Se lo añado" in second.text
    assert HelpRequest.objects.count() == 1
    assert "aparcamiento" in HelpRequest.objects.get().question


def test_health_questions_go_to_the_owner_even_if_the_ai_would_answer(salon, message_service):
    language_model_service = FakeLanguageModelService(json_response={"reply": "¡Claro! Sin problema.", "action": {"type": "none"}})

    reply = say(message_service, language_model_service, "web:salud", "Soy alérgica al látex, ¿puedo hacerme las pestañas?")

    assert HelpRequest.objects.count() == 1
    assert language_model_service.received == []
    assert "Sin problema" not in reply.text


def test_outcome_of_reads_what_really_happened():
    from application.shared.ai_receptionist import outcome_of
    from domain.entities.chat_reply import ChatButton, ChatReply

    assert outcome_of(ChatReply("hola")) == "text"
    assert outcome_of(ChatReply("elige", [[ChatButton("10:00", "slot:x:202610201000")]])) == "slots"
    assert outcome_of(ChatReply("¿cuál?", [[ChatButton("Uñas", "cat:nails")]])) == "choose_service"
