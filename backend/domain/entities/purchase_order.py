from decimal import Decimal

from django.db import models

from domain.entities.base_model import BaseModel


class PurchaseOrder(BaseModel):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    STATUS = [(DRAFT, "Borrador"), (SENT, "Enviado"), (RECEIVED, "Recibido"), (CANCELLED, "Cancelado")]
    OPEN_STATUSES = (DRAFT, SENT)

    supplier = models.ForeignKey("domain.Supplier", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=10, choices=STATUS, default=DRAFT)
    email_subject = models.CharField(max_length=200, blank=True)
    email_body = models.TextField(blank=True)
    written_by_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pedido"

    def __str__(self):
        return f"Pedido {self.pk} · {self.supplier}"

    @property
    def total(self):
        total = Decimal("0")
        for line in self.lines.all():
            total += line.units * line.unit_price
        return total


class PurchaseOrderLine(BaseModel):
    order = models.ForeignKey("domain.PurchaseOrder", on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("domain.Product", on_delete=models.PROTECT)
    units = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["order", "product"], name="unique_order_product")]

    @property
    def uses_added(self):
        return self.units * self.product.uses_per_unit
