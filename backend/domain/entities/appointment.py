from datetime import timedelta

from django.db import models

from domain.entities import payment
from domain.entities.base_model import BaseModel
from domain.exceptions import AppointmentNotActive


class Appointment(BaseModel):
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    STATUS = [
        (BOOKED, "Reservada"),
        (CONFIRMED, "Confirmada"),
        (COMPLETED, "Completada"),
        (CANCELLED, "Cancelada"),
        (NO_SHOW, "No vino"),
    ]
    ACTIVE_STATUSES = (BOOKED, CONFIRMED)

    SOURCE_WEB = "web"
    SOURCE_TELEGRAM = "telegram"
    SOURCE_OWNER = "owner"
    SOURCES = [(SOURCE_WEB, "Web"), (SOURCE_TELEGRAM, "Telegram"), (SOURCE_OWNER, "Mostrador")]

    client = models.ForeignKey("domain.Client", on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey("domain.Service", on_delete=models.PROTECT, related_name="appointments")
    start = models.DateTimeField("inicio")
    status = models.CharField(max_length=12, choices=STATUS, default=BOOKED)
    source = models.CharField(max_length=10, choices=SOURCES, default=SOURCE_OWNER)
    notes = models.TextField(blank=True)
    # Precio del servicio el día que se reservó: si luego cambia la tarifa, las cuentas pasadas no cambian
    price = models.DecimalField("precio", max_digits=8, decimal_places=2, null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    # Cobro: se rellena al completar la cita
    payment_method = models.CharField("forma de pago", max_length=10, choices=payment.METHODS, blank=True)
    pack = models.ForeignKey("domain.ClientPack", null=True, blank=True, on_delete=models.SET_NULL, related_name="appointments")
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]
        verbose_name = "cita"

    def __str__(self):
        return f"{self.client} · {self.service} · {self.start:%d/%m %H:%M}"

    @property
    def end(self):
        return self.start + timedelta(minutes=self.service.duration_minutes)

    @property
    def charged_price(self):
        return self.price if self.price is not None else self.service.price

    @property
    def cashed_amount(self):
        """Lo que entra en caja por esta cita: nada si se pagó con un bono (el bono ya se cobró al venderlo)."""
        return 0 if self.payment_method == payment.PACK else self.charged_price

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    def ensure_active(self):
        if not self.is_active:
            raise AppointmentNotActive()
