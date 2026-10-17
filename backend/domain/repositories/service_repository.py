from abc import ABC, abstractmethod


class ServiceRepository(ABC):
    @abstractmethod
    def get(self, service_id):
        """Devuelve el servicio o lanza Service.DoesNotExist."""

    @abstractmethod
    def find_active(self, service_id):
        """Servicio activo o None (también None si el id no es válido)."""

    @abstractmethod
    def list(self, only_active=False):
        pass

    @abstractmethod
    def list_consumption(self, service):
        """Productos que gasta el servicio, con cuántos usos de cada uno."""

    @abstractmethod
    def add_consumption(self, service, product, uses):
        """Ese servicio gasta 'uses' usos del producto cada vez."""

    @abstractmethod
    def create(self, **fields):
        pass

    @abstractmethod
    def save(self, service, fields):
        pass
