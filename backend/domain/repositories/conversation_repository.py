from abc import ABC, abstractmethod


class ConversationRepository(ABC):
    @abstractmethod
    def get(self, conversation_id):
        pass

    @abstractmethod
    def get_or_create(self, key, client=None):
        """Busca la conversación por clave y le asigna la clienta si se pasa."""

    @abstractmethod
    def save(self, conversation, fields):
        pass

    @abstractmethod
    def add_message(self, conversation, role, text, by_ai=False, from_owner=False):
        pass

    @abstractmethod
    def last_messages(self, conversation, limit):
        """Últimos mensajes en orden de lectura (del más antiguo al más nuevo)."""

    @abstractmethod
    def list_recent(self, limit):
        pass

    @abstractmethod
    def last_message_for_key(self, key):
        pass

    @abstractmethod
    def owner_messages_after(self, key, after_message_id=None):
        """Mensajes escritos por la dueña en esa conversación después de un mensaje dado."""
