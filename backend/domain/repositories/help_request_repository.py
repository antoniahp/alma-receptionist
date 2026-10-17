from abc import ABC, abstractmethod


class HelpRequestRepository(ABC):
    @abstractmethod
    def get(self, help_request_id):
        """Devuelve la pregunta o lanza HelpRequest.DoesNotExist."""

    @abstractmethod
    def find_open_for_conversation(self, conversation):
        pass

    @abstractmethod
    def find_by_owner_message_id(self, message_id):
        pass

    @abstractmethod
    def create(self, conversation, client, question, contact):
        pass

    @abstractmethod
    def save(self, help_request, fields):
        pass

    @abstractmethod
    def list(self, statuses=None, limit=50):
        pass

    @abstractmethod
    def last_open(self):
        """La última pregunta sin contestar, o None."""

    @abstractmethod
    def count_open(self):
        pass
