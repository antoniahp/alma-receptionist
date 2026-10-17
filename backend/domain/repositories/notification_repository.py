from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, kind, text, status, client_id=None, error="", appointment_id=None, service_id=None, telegram_message_id=""):
        pass

    @abstractmethod
    def list_recent(self, limit):
        pass

    @abstractmethod
    def reactivation_sent_since(self, client_id, service_id, since):
        """True si ya se le escribió para repetir ese servicio después de esa fecha."""
