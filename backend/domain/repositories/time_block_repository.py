from abc import ABC, abstractmethod


class TimeBlockRepository(ABC):
    @abstractmethod
    def create(self, start, end, reason):
        pass

    @abstractmethod
    def get(self, block_id):
        """Devuelve el bloqueo o lanza TimeBlock.DoesNotExist."""

    @abstractmethod
    def delete(self, block):
        pass

    @abstractmethod
    def list_overlapping(self, start, end):
        """Bloqueos que pisan el intervalo [start, end)."""
