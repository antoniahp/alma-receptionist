"""Cobros: forma de pago, bonos, deshacer "Completar" y cierre de caja."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from model_bakery import baker

from application.commands.close_cash.command import CloseCashCommand
from application.commands.close_cash.command_dto import CloseCashCommandDTO
from application.commands.complete_appointment.command import CompleteAppointmentCommand
from application.commands.complete_appointment.command_dto import CompleteAppointmentCommandDTO
from application.commands.sell_pack.command import SellPackCommand
from application.commands.sell_pack.command_dto import SellPackCommandDTO
from application.commands.undo_complete_appointment.command import UndoCompleteAppointmentCommand
from application.commands.undo_complete_appointment.command_dto import UndoCompleteAppointmentCommandDTO
from application.queries.get_cash_day.query import GetCashDayQuery
from application.queries.get_cash_day.query_dto import GetCashDayQueryDTO
from domain.entities import Appointment, payment
from domain.exceptions import CannotUndo, CashAlreadyClosed, InvalidPayment, NoActivePack

pytestmark = pytest.mark.django_db


def appointment_today(salon, price="45"):
    start = timezone.localtime().replace(hour=10, minute=0, second=0, microsecond=0)
    return baker.make(Appointment, client=salon.laura, service=salon.massage, start=start, price=Decimal(price))


def complete(repositories, appointment, method):
    return CompleteAppointmentCommand(repositories).execute(
        CompleteAppointmentCommandDTO(appointment_id=appointment.id, payment_method=method)
    )


def sell_pack(repositories, salon, sessions=5, price="200", method=payment.CARD):
    return SellPackCommand(repositories).execute(
        SellPackCommandDTO(
            client_id=salon.laura.id, service_id=salon.massage.id, sessions=sessions, price=Decimal(price), payment_method=method
        )
    )


def test_completing_saves_how_it_was_paid(repositories, salon):
    appointment, _ = complete(repositories, appointment_today(salon), payment.BIZUM)

    assert appointment.payment_method == payment.BIZUM
    assert appointment.completed_at is not None


def test_unknown_payment_method_is_rejected(repositories, salon):
    with pytest.raises(InvalidPayment):
        complete(repositories, appointment_today(salon), "cheque")


def test_paying_with_a_pack_uses_one_session(repositories, salon):
    pack = sell_pack(repositories, salon, sessions=5)

    appointment, _ = complete(repositories, appointment_today(salon), payment.PACK)

    pack.refresh_from_db()
    assert pack.sessions_left == 4
    assert appointment.pack == pack
    assert appointment.cashed_amount == 0


def test_without_a_pack_you_cannot_pay_with_a_pack(repositories, salon):
    with pytest.raises(NoActivePack):
        complete(repositories, appointment_today(salon), payment.PACK)


def test_undo_gives_back_the_product_and_the_session(repositories, salon):
    pack = sell_pack(repositories, salon)
    salon.oil.refresh_from_db()
    stock_before = salon.oil.stock_uses
    appointment, _ = complete(repositories, appointment_today(salon), payment.PACK)

    undone = UndoCompleteAppointmentCommand(repositories).execute(UndoCompleteAppointmentCommandDTO(appointment_id=appointment.id))

    pack.refresh_from_db()
    salon.oil.refresh_from_db()
    assert undone.status == Appointment.BOOKED
    assert undone.payment_method == ""
    assert pack.sessions_used == 0
    assert salon.oil.stock_uses == stock_before


def test_undo_is_only_possible_for_a_few_minutes(repositories, salon):
    appointment, _ = complete(repositories, appointment_today(salon), payment.CASH)
    appointment.completed_at = timezone.now() - timedelta(minutes=30)
    appointment.save()

    with pytest.raises(CannotUndo):
        UndoCompleteAppointmentCommand(repositories).execute(UndoCompleteAppointmentCommandDTO(appointment_id=appointment.id))


def test_cash_day_and_closing(repositories, salon):
    complete(repositories, appointment_today(salon, "45"), payment.CASH)
    complete(repositories, appointment_today(salon, "30"), payment.CARD)
    sell_pack(repositories, salon, price="200", method=payment.CASH)
    complete(repositories, appointment_today(salon, "45"), payment.PACK)
    today = timezone.localdate()

    cash_day = GetCashDayQuery(repositories).execute(GetCashDayQueryDTO(day=today))

    assert cash_day["cash"] == Decimal("245")
    assert cash_day["card"] == Decimal("30")
    assert cash_day["sessions_with_pack"] == 1
    assert [charge["payment_method"] for charge in cash_day["charges"]].count(payment.CASH) == 2
    assert len(cash_day["charges"]) == 4

    closing = CloseCashCommand(repositories).execute(CloseCashCommandDTO(day=today, counted_cash=Decimal("240")))
    assert closing.difference == Decimal("-5")

    with pytest.raises(CashAlreadyClosed):
        CloseCashCommand(repositories).execute(CloseCashCommandDTO(day=today, counted_cash=Decimal("240")))
