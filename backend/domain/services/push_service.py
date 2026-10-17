from abc import ABC, abstractmethod


class PushService(ABC):
    """Avisos emergentes del navegador (Web Push) para la dueña."""

    @abstractmethod
    def is_enabled(self):
        """False si faltan las claves VAPID: entonces no se envía nada."""

    @abstractmethod
    def public_key(self):
        """Clave pública que necesita el navegador para suscribirse."""

    @abstractmethod
    def send(self, subscription, title, body, url):
        """Envía un aviso a un navegador. Lanza PushSubscriptionExpired si ese navegador ya no lo acepta."""
