from django.db import models

from domain.entities.base_model import BaseModel


class ShoppingListItem(BaseModel):
    """Una oferta que la dueña ha elegido en el comparador de precios para comprarla."""

    product = models.ForeignKey("domain.Product", on_delete=models.CASCADE, related_name="shopping_list_items")
    store = models.CharField("tienda", max_length=120)
    title = models.CharField("producto en la tienda", max_length=300, blank=True)
    price = models.DecimalField("precio", max_digits=8, decimal_places=2)
    link = models.CharField(max_length=2000, blank=True)
    units = models.PositiveIntegerField("unidades", default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["store", "created_at"]
        verbose_name = "producto en la lista de compra"
        verbose_name_plural = "lista de compra"
        constraints = [models.UniqueConstraint(fields=["product", "store"], name="unique_product_store")]

    def __str__(self):
        return f"{self.units} × {self.product} en {self.store}"

    @property
    def total(self):
        return self.units * self.price
