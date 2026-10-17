from abc import ABC, abstractmethod


class CashClosingRepository(ABC):
    @abstractmethod
    def find_for_day(self, day):
        pass

    @abstractmethod
    def create(self, day, expected_cash, counted_cash, card_total, bizum_total, notes):
        pass
