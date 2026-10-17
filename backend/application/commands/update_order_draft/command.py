from domain.entities import PurchaseOrder
from domain.exceptions import OrderNotDraft


class UpdateOrderDraftCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        order = self.repositories.purchase_orders.get(dto.order_id)
        if order.status != PurchaseOrder.DRAFT:
            raise OrderNotDraft()
        order.email_subject = dto.email_subject.strip()[:200]
        order.email_body = dto.email_body.strip()
        self.repositories.purchase_orders.save(order, ["email_subject", "email_body"])
        return order
