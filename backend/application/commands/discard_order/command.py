from domain.entities import PurchaseOrder
from domain.exceptions import OrderNotDraft


class DiscardOrderCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        order = self.repositories.purchase_orders.get(dto.order_id)
        if order.status != PurchaseOrder.DRAFT:
            raise OrderNotDraft()
        order.status = PurchaseOrder.CANCELLED
        self.repositories.purchase_orders.save(order, ["status"])
        return order
