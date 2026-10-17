from abc import ABC, abstractmethod


class PurchaseOrderRepository(ABC):
    @abstractmethod
    def get(self, order_id):
        """Devuelve el pedido o lanza PurchaseOrder.DoesNotExist."""

    @abstractmethod
    def get_for_update(self, order_id):
        pass

    @abstractmethod
    def find_draft_for_supplier(self, supplier):
        pass

    @abstractmethod
    def create(self, supplier):
        pass

    @abstractmethod
    def set_line(self, order, product, units, unit_price):
        """Crea o actualiza la línea de ese producto en el pedido."""

    @abstractmethod
    def lines(self, order):
        pass

    @abstractmethod
    def save(self, order, fields):
        pass

    @abstractmethod
    def list(self, statuses=None):
        pass

    @abstractmethod
    def product_ids_in_open_orders(self):
        pass

    @abstractmethod
    def count_drafts(self):
        pass

    @abstractmethod
    def list_ordered_between(self, start, end):
        """Pedidos enviados (o ya recibidos) cuya fecha de envío está entre start y end."""
