from domain.entities import PurchaseOrder, PurchaseOrderLine
from domain.repositories.purchase_order_repository import PurchaseOrderRepository


class DjangoPurchaseOrderRepository(PurchaseOrderRepository):
    def base_queryset(self):
        return PurchaseOrder.objects.select_related("supplier").prefetch_related("lines__product")

    def get(self, order_id):
        return self.base_queryset().get(pk=order_id)

    def get_for_update(self, order_id):
        return PurchaseOrder.objects.select_for_update().select_related("supplier").get(pk=order_id)

    def find_draft_for_supplier(self, supplier):
        return PurchaseOrder.objects.filter(supplier=supplier, status=PurchaseOrder.DRAFT).first()

    def create(self, supplier):
        return PurchaseOrder.objects.create(supplier=supplier)

    def set_line(self, order, product, units, unit_price):
        PurchaseOrderLine.objects.update_or_create(order=order, product=product, defaults={"units": units, "unit_price": unit_price})

    def lines(self, order):
        return list(order.lines.select_related("product"))

    def save(self, order, fields):
        order.save(update_fields=fields)

    def list(self, statuses=None):
        orders = self.base_queryset()
        if statuses:
            orders = orders.filter(status__in=statuses)
        return list(orders)

    def list_ordered_between(self, start, end):
        orders = self.base_queryset().filter(status__in=[PurchaseOrder.SENT, PurchaseOrder.RECEIVED], sent_at__gte=start, sent_at__lt=end)
        return list(orders.order_by("sent_at"))

    def product_ids_in_open_orders(self):
        lines = PurchaseOrderLine.objects.filter(order__status__in=PurchaseOrder.OPEN_STATUSES)
        return set(lines.values_list("product_id", flat=True))

    def count_drafts(self):
        return PurchaseOrder.objects.filter(status=PurchaseOrder.DRAFT).count()
