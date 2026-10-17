from abc import ABC, abstractmethod


class SupplierRepository(ABC):
    @abstractmethod
    def get(self, supplier_id):
        """Devuelve el proveedor o lanza Supplier.DoesNotExist."""

    @abstractmethod
    def save(self, supplier, fields):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def create(self, name):
        pass
