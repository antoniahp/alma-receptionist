from abc import ABC, abstractmethod


class EmailService(ABC):
    @abstractmethod
    def send(self, to, subject, body):
        """Envía un correo. Lanza MessageNotSent si falla."""
