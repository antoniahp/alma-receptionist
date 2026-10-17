from django.db import models

from domain.entities.base_model import BaseModel


class CashClosing(BaseModel):
    """Cierre de caja de un día: lo que debería haber en efectivo y lo que se ha contado."""

    day = models.DateField("día", unique=True)
    expected_cash = models.DecimalField("efectivo esperado", max_digits=10, decimal_places=2)
    counted_cash = models.DecimalField("efectivo contado", max_digits=10, decimal_places=2)
    card_total = models.DecimalField("tarjeta", max_digits=10, decimal_places=2)
    bizum_total = models.DecimalField("Bizum", max_digits=10, decimal_places=2)
    notes = models.TextField("notas", blank=True)
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-day"]
        verbose_name = "cierre de caja"

    @property
    def difference(self):
        return self.counted_cash - self.expected_cash
