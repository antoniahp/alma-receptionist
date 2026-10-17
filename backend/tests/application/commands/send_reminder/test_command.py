from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.commands.send_reminder.command import SendReminderCommand
from application.commands.send_reminder.command_dto import SendReminderCommandDTO
from domain.entities import Appointment, Notification
from tests.fakes import FakeMessageService

pytestmark = pytest.mark.django_db


def test_simulated_when_client_has_not_opened_the_bot(repositories, salon, message_service):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(hours=20))

    notification = SendReminderCommand(repositories, message_service).execute(SendReminderCommandDTO(appointment_id=appointment.id))

    appointment.refresh_from_db()
    assert notification.status == Notification.SIMULATED
    assert "Laura" in notification.text
    assert appointment.reminder_sent_at is not None


def test_sent_by_telegram_with_buttons(repositories, salon, message_service):
    salon.laura.telegram_chat_id = "555"
    salon.laura.save()
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(hours=20))

    notification = SendReminderCommand(repositories, message_service).execute(SendReminderCommandDTO(appointment_id=appointment.id))

    assert notification.status == Notification.SENT
    sent = message_service.sent[0]
    assert sent["chat_id"] == "555"
    assert [button.data for button in sent["buttons"][0]] == [f"confirm:{appointment.id}", f"change:{appointment.id}"]


def test_failed_send_keeps_reminder_pending(repositories, salon):
    salon.laura.telegram_chat_id = "555"
    salon.laura.save()
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(hours=20))

    notification = SendReminderCommand(repositories, FakeMessageService(fail=True)).execute(
        SendReminderCommandDTO(appointment_id=appointment.id)
    )

    appointment.refresh_from_db()
    assert notification.status == Notification.FAILED
    assert appointment.reminder_sent_at is None
