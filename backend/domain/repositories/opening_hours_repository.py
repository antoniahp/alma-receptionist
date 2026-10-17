from abc import ABC, abstractmethod


class OpeningHoursRepository(ABC):
    @abstractmethod
    def list_all(self):
        pass

    @abstractmethod
    def list_for_weekday(self, weekday):
        pass

    @abstractmethod
    def lock_weekday(self, weekday):
        """Bloquea el horario de ese día de la semana mientras dura la transacción (evita reservas dobles)."""

    @abstractmethod
    def is_open(self, weekday):
        pass
