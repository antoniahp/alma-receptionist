from abc import ABC, abstractmethod


class MessageService(ABC):
    """Envía mensajes a un chat (Telegram)."""

    @abstractmethod
    def is_enabled(self):
        """True si el servicio está configurado."""

    @abstractmethod
    def send(self, chat_id, text, buttons=None):
        """Envía el texto con botones opcionales (filas de ChatButton). Devuelve el id del mensaje.

        Lanza MessageNotSent si no se puede enviar.
        """
