from django.db import transaction
from django.utils import timezone

from domain.entities import PurchaseOrder
from domain.exceptions import OrderNotDraft


class ApproveOrderCommand:
    """La dueña aprueba el borrador: se envía el correo al proveedor."""

    def __init__(self, repositories, email_service):
        self.repositories = repositories
        self.email_service = email_service

    def execute(self, dto):
        with transaction.atomic():
            order = self.repositories.purchase_orders.get_for_update(dto.order_id)
            if order.status != PurchaseOrder.DRAFT:
                raise OrderNotDraft()
            if order.supplier.email:
                self.email_service.send(order.supplier.email, order.email_subject or "Pedido", order.email_body)
            order.status = PurchaseOrder.SENT
            order.sent_at = timezone.now()
            self.repositories.purchase_orders.save(order, ["status", "sent_at"])
        return self.repositories.purchase_orders.get(order.id)
