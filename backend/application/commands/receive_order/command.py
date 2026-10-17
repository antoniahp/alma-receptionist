from django.db import transaction
from django.utils import timezone

from domain.entities import PurchaseOrder, StockMovement
from domain.exceptions import OrderNotSent


class ReceiveOrderCommand:
    """Ha llegado la caja: se suma el stock de cada línea."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        with transaction.atomic():
            order = self.repositories.purchase_orders.get_for_update(dto.order_id)
            if order.status != PurchaseOrder.SENT:
                raise OrderNotSent()
            for line in self.repositories.purchase_orders.lines(order):
                self.repositories.products.change_stock(line.product, line.uses_added, StockMovement.REASON_ORDER_RECEIVED, order=order)
            order.status = PurchaseOrder.RECEIVED
            order.received_at = timezone.now()
            self.repositories.purchase_orders.save(order, ["status", "received_at"])
        return self.repositories.purchase_orders.get(order.id)
