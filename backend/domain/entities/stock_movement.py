from django.db import models

from domain.entities.base_model import BaseModel


class StockMovement(BaseModel):
    """Historial de entradas y salidas de stock (sirve para previsiones futuras)."""

    REASON_APPOINTMENT = "cita"
    REASON_ORDER_RECEIVED = "pedido recibido"
    REASON_UNDO = "deshacer cita completada"

    product = models.ForeignKey("domain.Product", on_delete=models.CASCADE, related_name="movements")
    change = models.IntegerField("cambio en usos")
    reason = models.CharField(max_length=40)
    appointment = models.ForeignKey("domain.Appointment", null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey("domain.PurchaseOrder", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
