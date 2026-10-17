from abc import ABC, abstractmethod


class ClientRepository(ABC):
    @abstractmethod
    def get(self, client_id):
        """Devuelve la clienta o lanza Client.DoesNotExist."""

    @abstractmethod
    def find(self, client_id):
        """Devuelve la clienta o None."""

    @abstractmethod
    def find_by_phone(self, phone):
        pass

    @abstractmethod
    def find_by_telegram_chat(self, chat_id):
        pass

    @abstractmethod
    def find_by_link_code(self, link_code):
        pass

    @abstractmethod
    def create(self, name, phone="", telegram_chat_id=None, email="", notes=""):
        pass

    @abstractmethod
    def save(self, client, fields):
        pass

    @abstractmethod
    def search(self, text=""):
        """Clientas con sus visitas (visits_count, last_visit) y su próxima cita (next_visit)."""

    @abstractmethod
    def get_many(self, client_ids):
        """Diccionario {id: clienta}."""

    @abstractmethod
    def list_review_candidates(self, completed_before, min_visits):
        """Clientas con Telegram, sin reseña pedida, con al menos min_visits citas completadas
        y cuya última cita fue antes de completed_before."""

    @abstractmethod
    def forget(self, client):
        """Borra sus datos personales, sus conversaciones y sus mensajes. Las citas se quedan (sin nombre) para las cuentas."""
