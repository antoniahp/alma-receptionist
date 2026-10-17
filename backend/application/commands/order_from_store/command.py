from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domain.entities import PurchaseOrder
from domain.exceptions import ShoppingListEmpty
from domain.rules import customer_messages
from domain.rules.price_matching import supplier_for_store


class OrderFromStoreCommand:
    """Convierte lo elegido de una tienda en un pedido.

    - Si es un proveedor y se quiere pedir por correo: queda un borrador para revisar y aprobar (con aviso antes de enviar).
    - Si ya lo ha comprado en la web de la tienda: queda como pedido en camino, para marcarlo como recibido al llegar.
    """

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        items = self.repositories.shopping_list.list_for_store(dto.store)
        if not items:
            raise ShoppingListEmpty()

        with transaction.atomic():
            supplier = supplier_for_store(self.repositories.suppliers.list(), dto.store)
            if supplier is None:
                supplier = self.repositories.suppliers.create(dto.store)
            order = self.repositories.purchase_orders.find_draft_for_supplier(supplier)
            if order is None:
                order = self.repositories.purchase_orders.create(supplier)
            for item in items:
                self.repositories.purchase_orders.set_line(order, item.product, item.units, item.price)

            if dto.bought_online:
                order.status = PurchaseOrder.SENT
                order.sent_at = timezone.now()
                order.email_subject = f"Compra online en {dto.store}"
                self.repositories.purchase_orders.save(order, ["status", "sent_at", "email_subject"])
            else:
                lines = [(line.product, line.units) for line in self.repositories.purchase_orders.lines(order)]
                order.email_subject, order.email_body = customer_messages.order_email(settings.BUSINESS, supplier, lines)
                order.written_by_ai = False
                self.repositories.purchase_orders.save(order, ["email_subject", "email_body", "written_by_ai"])

            for item in items:
                self.repositories.shopping_list.delete(item)
        return self.repositories.purchase_orders.get(order.id)
