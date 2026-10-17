from django.db import models

from domain.entities.base_model import BaseModel


class Product(BaseModel):
    """Producto que gastan los servicios. El stock se cuenta en usos (p. ej. una botella = 5 masajes)."""

    name = models.CharField("nombre", max_length=160)
    reference = models.CharField("referencia", max_length=40, blank=True)
    supplier = models.ForeignKey("domain.Supplier", on_delete=models.PROTECT, related_name="products")
    unit_price = models.DecimalField("precio por unidad", max_digits=8, decimal_places=2, default=0)
    uses_per_unit = models.PositiveIntegerField("usos por unidad", default=1)
    stock_uses = models.IntegerField("usos en stock", default=0)
    min_uses = models.PositiveIntegerField("mínimo de usos", default=2)

    class Meta:
        ordering = ["name"]
        verbose_name = "producto"

    def __str__(self):
        return self.name
