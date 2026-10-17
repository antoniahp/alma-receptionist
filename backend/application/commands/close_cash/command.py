from django.db import IntegrityError, transaction

from application.queries.get_cash_day.query import GetCashDayQuery
from application.queries.get_cash_day.query_dto import GetCashDayQueryDTO
from domain.exceptions import CashAlreadyClosed, InvalidPayment


class CloseCashCommand:
    """Cierre de caja: se apunta lo que debería haber en efectivo y lo que se ha contado."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if dto.counted_cash < 0:
            raise InvalidPayment("El efectivo contado no puede ser negativo.")
        cash_day = GetCashDayQuery(self.repositories).execute(GetCashDayQueryDTO(day=dto.day))
        if cash_day["closing"]:
            raise CashAlreadyClosed()
        try:
            with transaction.atomic():
                return self.repositories.cash_closings.create(
                    day=dto.day,
                    expected_cash=cash_day["cash"],
                    counted_cash=dto.counted_cash,
                    card_total=cash_day["card"],
                    bizum_total=cash_day["bizum"],
                    notes=dto.notes.strip(),
                )
        except IntegrityError as error:  # dos cierres a la vez del mismo día
            raise CashAlreadyClosed() from error
