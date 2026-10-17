from abc import ABC, abstractmethod


class PushSubscriptionRepository(ABC):
    @abstractmethod
    def save(self, endpoint, p256dh, auth):
        """Guarda la suscripción del navegador (si ya existía, actualiza sus claves)."""

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def delete_by_endpoint(self, endpoint):
        pass
