"""Bloqueos de agenda, tratamientos, ficha de clienta, borrado de datos y reseñas."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from model_bakery import baker

from application.commands.book_online_appointment.command import BookOnlineAppointmentCommand
from application.commands.book_online_appointment.command_dto import BookOnlineAppointmentCommandDTO
from application.commands.create_service.command import CreateServiceCommand
from application.commands.create_service.command_dto import CreateServiceCommandDTO
from application.commands.create_time_block.command import CreateTimeBlockCommand
from application.commands.create_time_block.command_dto import CreateTimeBlockCommandDTO
from application.commands.forget_client.command import ForgetClientCommand
from application.commands.forget_client.command_dto import ForgetClientCommandDTO
from application.commands.send_review_requests.command import SendReviewRequestsCommand
from application.commands.send_review_requests.command_dto import SendReviewRequestsCommandDTO
from application.commands.update_service.command import UpdateServiceCommand
from application.commands.update_service.command_dto import UpdateServiceCommandDTO
from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from application.queries.get_client_file.query import GetClientFileQuery
from application.queries.get_client_file.query_dto import GetClientFileQueryDTO
from domain.entities import Appointment, Client, Conversation, Notification
from domain.exceptions import DomainError, InvalidServiceData, InvalidTimeBlock, PrivacyNotAccepted
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def slot_hours(repositories, salon, day):
    slots = GetAvailableSlotsQuery(repositories).execute(GetAvailableSlotsQueryDTO(service_id=salon.massage.id, day=day))
    return [f"{timezone.localtime(slot):%H:%M}" for slot in slots]


def test_blocked_hours_are_not_offered(repositories, salon, next_monday):
    CreateTimeBlockCommand(repositories).execute(
        CreateTimeBlockCommandDTO(start=local_datetime(next_monday, 10), end=local_datetime(next_monday, 12), reason="Médico")
    )

    hours = slot_hours(repositories, salon, next_monday)

    assert "10:00" not in hours
    assert "11:30" not in hours
    assert "12:00" in hours


def test_a_block_must_end_after_it_starts(repositories, next_monday):
    with pytest.raises(InvalidTimeBlock):
        CreateTimeBlockCommand(repositories).execute(
            CreateTimeBlockCommandDTO(start=local_datetime(next_monday, 12), end=local_datetime(next_monday, 10))
        )


def service_dto(**changes):
    data = {"name": "Lifting de pestañas", "category": "cejas_pestanas", "price": Decimal("35"), "duration_minutes": 60}
    return CreateServiceCommandDTO(**{**data, **changes})


def test_create_and_update_a_treatment(repositories, salon):
    service = CreateServiceCommand(repositories).execute(service_dto())

    updated = UpdateServiceCommand(repositories).execute(
        UpdateServiceCommandDTO(
            service_id=service.id, name="Lifting", category="cejas_pestanas", price=Decimal("38"), duration_minutes=45, active=False
        )
    )

    assert updated.price == Decimal("38")
    assert updated.active is False


def test_treatment_with_a_wrong_duration_is_rejected(repositories):
    with pytest.raises(InvalidServiceData):
        CreateServiceCommand(repositories).execute(service_dto(duration_minutes=5))


def test_changing_the_price_keeps_the_price_of_booked_appointments(repositories, salon, next_monday):
    appointment = repositories.appointments.create(salon.laura, salon.massage, local_datetime(next_monday, 10), Appointment.SOURCE_OWNER)

    UpdateServiceCommand(repositories).execute(
        UpdateServiceCommandDTO(
            service_id=salon.massage.id,
            name=salon.massage.name,
            category=salon.massage.category,
            price=Decimal("99"),
            duration_minutes=salon.massage.duration_minutes,
            active=True,
        )
    )

    appointment.refresh_from_db()
    assert appointment.charged_price == salon.massage.price != Decimal("99")


def test_client_file_has_history_and_total_spent(repositories, salon):
    baker.make(
        Appointment,
        client=salon.laura,
        service=salon.massage,
        start=timezone.now() - timedelta(days=10),
        status=Appointment.COMPLETED,
        price=Decimal("45"),
    )

    client_file = GetClientFileQuery(repositories).execute(GetClientFileQueryDTO(client_id=salon.laura.id))

    assert client_file["visits"] == 1
    assert client_file["spent"] == Decimal("45")
    assert len(client_file["appointments"]) == 1


def test_forget_client_removes_personal_data_but_keeps_the_accounts(repositories, salon):
    baker.make(
        Appointment, client=salon.laura, service=salon.massage, start=timezone.now() - timedelta(days=10), status=Appointment.COMPLETED
    )
    baker.make(Conversation, client=salon.laura, key="web:abc")

    ForgetClientCommand(repositories).execute(ForgetClientCommandDTO(client_id=salon.laura.id))

    client = Client.objects.get(pk=salon.laura.id)
    assert client.name == "Clienta borrada"
    assert client.phone == ""
    assert client.telegram_chat_id is None
    assert not Conversation.objects.filter(key="web:abc").exists()
    assert client.appointments.count() == 1


def test_cannot_forget_a_client_with_upcoming_appointments(repositories, salon):
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(days=2))

    with pytest.raises(DomainError):
        ForgetClientCommand(repositories).execute(ForgetClientCommandDTO(client_id=salon.laura.id))


def test_online_booking_needs_the_privacy_policy(repositories, salon, next_monday, message_service):
    with pytest.raises(PrivacyNotAccepted):
        BookOnlineAppointmentCommand(repositories, message_service).execute(
            BookOnlineAppointmentCommandDTO(service_id=salon.massage.id, start=local_datetime(next_monday, 10), name="Irene", phone="699")
        )


def test_online_booking_saves_when_privacy_was_accepted(repositories, salon, next_monday, message_service):
    appointment = BookOnlineAppointmentCommand(repositories, message_service).execute(
        BookOnlineAppointmentCommandDTO(
            service_id=salon.massage.id, start=local_datetime(next_monday, 10), name="Irene", phone="699", privacy_accepted=True
        )
    )

    assert appointment.client.privacy_accepted_at is not None


def completed_visits(client, service, how_many):
    """Citas completadas: la última ayer y las anteriores una por semana."""
    for days_ago in [1, 8, 15, 22][:how_many]:
        baker.make(
            Appointment, client=client, service=service, start=timezone.now() - timedelta(days=days_ago), status=Appointment.COMPLETED
        )


def test_review_is_asked_once_the_day_after_the_third_visit(repositories, salon, message_service, settings):
    settings.GOOGLE_REVIEW_URL = "https://g.page/r/alma/review"
    salon.laura.telegram_chat_id = "123"
    salon.laura.save()
    completed_visits(salon.laura, salon.massage, 3)

    sent = SendReviewRequestsCommand(repositories, message_service).execute(SendReviewRequestsCommandDTO())
    sent_again = SendReviewRequestsCommand(repositories, message_service).execute(SendReviewRequestsCommandDTO())

    assert sent == 1
    assert sent_again == 0
    assert Notification.objects.filter(kind=Notification.REVIEW, client=salon.laura).count() == 1
    assert "https://g.page/r/alma/review" in message_service.sent[-1]["text"]


def test_review_is_not_asked_after_two_visits_or_on_the_same_day(repositories, salon, message_service, settings):
    settings.GOOGLE_REVIEW_URL = "https://g.page/r/alma/review"
    salon.laura.telegram_chat_id = "123"
    salon.laura.save()
    completed_visits(salon.laura, salon.massage, 2)
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now(), status=Appointment.COMPLETED)

    assert SendReviewRequestsCommand(repositories, message_service).execute(SendReviewRequestsCommandDTO()) == 0


def test_without_review_link_nothing_is_sent(repositories, salon, message_service):
    salon.laura.telegram_chat_id = "123"
    salon.laura.save()
    completed_visits(salon.laura, salon.massage, 3)

    assert SendReviewRequestsCommand(repositories, message_service).execute(SendReviewRequestsCommandDTO()) == 0
