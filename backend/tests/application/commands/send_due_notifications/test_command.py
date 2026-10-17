from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.commands.send_due_notifications.command import SendDueNotificationsCommand
from application.commands.send_due_notifications.command_dto import SendDueNotificationsCommandDTO
from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_sends_reminders_and_reactivations_in_working_hours(repositories, salon, message_service, language_model_service):
    noon = timezone.localtime().replace(hour=12, minute=0, second=0, microsecond=0)
    salon.laura.telegram_chat_id = "555"
    salon.laura.save()
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=noon + timedelta(hours=20))
    other = baker.make("domain.Client", name="Marta Ruiz", telegram_chat_id="556")
    baker.make(Appointment, client=other, service=salon.massage, status=Appointment.COMPLETED, start=noon - timedelta(days=31))

    sent = SendDueNotificationsCommand(repositories, message_service, language_model_service).execute(
        SendDueNotificationsCommandDTO(now=noon)
    )

    assert sent == {"reminders": 1, "reactivations": 1, "reviews": 0}


def test_no_reactivations_at_night(repositories, salon, message_service, language_model_service):
    night = timezone.localtime().replace(hour=22, minute=0, second=0, microsecond=0)
    baker.make(Appointment, client=salon.laura, service=salon.massage, status=Appointment.COMPLETED, start=night - timedelta(days=31))

    sent = SendDueNotificationsCommand(repositories, message_service, language_model_service).execute(
        SendDueNotificationsCommandDTO(now=night)
    )

    assert sent["reactivations"] == 0


def test_clients_without_telegram_stay_pending(repositories, salon, message_service, language_model_service):
    noon = timezone.localtime().replace(hour=12, minute=0, second=0, microsecond=0)
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=noon + timedelta(hours=20))

    sent = SendDueNotificationsCommand(repositories, message_service, language_model_service).execute(
        SendDueNotificationsCommandDTO(now=noon)
    )

    appointment.refresh_from_db()
    assert sent["reminders"] == 0
    assert appointment.reminder_sent_at is None
