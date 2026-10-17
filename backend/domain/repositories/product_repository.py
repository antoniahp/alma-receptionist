from abc import ABC, abstractmethod


class ProductRepository(ABC):
    @abstractmethod
    def get(self, product_id):
        """Devuelve el producto o lanza Product.DoesNotExist."""

    @abstractmethod
    def list_with_supplier(self):
        pass

    @abstractmethod
    def change_stock(self, product, uses, reason, appointment=None, order=None):
        """Suma (o resta, si es negativo) usos al stock y guarda el movimiento."""

    @abstractmethod
    def create(self, name, supplier, unit_price, uses_per_unit, stock_uses, min_uses, reference=""):
        pass

    @abstractmethod
    def movements_for_appointment(self, appointment):
        """Lo que se descontó del stock al completar esa cita."""
