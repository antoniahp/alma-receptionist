from django.db import models

from domain.entities.base_model import BaseModel


class ClientPack(BaseModel):
    """Bono de sesiones que compra una clienta (por ejemplo, 5 sesiones de depilación de piernas)."""

    client = models.ForeignKey("domain.Client", on_delete=models.CASCADE, related_name="packs")
    service = models.ForeignKey("domain.Service", on_delete=models.PROTECT, related_name="packs")
    sessions_total = models.PositiveIntegerField("sesiones")
    sessions_used = models.PositiveIntegerField("sesiones gastadas", default=0)
    price = models.DecimalField("precio del bono", max_digits=8, decimal_places=2)
    payment_method = models.CharField("forma de pago", max_length=10)
    sold_at = models.DateTimeField("vendido el")

    class Meta:
        ordering = ["-sold_at"]
        verbose_name = "bono"

    def __str__(self):
        return f"{self.client} · {self.service} · {self.sessions_left} de {self.sessions_total}"

    @property
    def sessions_left(self):
        return self.sessions_total - self.sessions_used

    @property
    def is_active(self):
        return self.sessions_left > 0
