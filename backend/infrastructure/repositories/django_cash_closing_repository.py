from domain.entities import CashClosing
from domain.repositories.cash_closing_repository import CashClosingRepository


class DjangoCashClosingRepository(CashClosingRepository):
    def find_for_day(self, day):
        return CashClosing.objects.filter(day=day).first()

    def create(self, day, expected_cash, counted_cash, card_total, bizum_total, notes):
        return CashClosing.objects.create(
            day=day, expected_cash=expected_cash, counted_cash=counted_cash, card_total=card_total, bizum_total=bizum_total, notes=notes
        )
