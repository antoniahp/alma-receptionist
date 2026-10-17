from django.db import models

from domain.entities.base_model import BaseModel


class Notification(BaseModel):
    """Registro de cada mensaje enviado (o simulado) a una clienta o a la dueña."""

    REMINDER = "reminder"
    REACTIVATION = "reactivation"
    CONFIRMATION = "confirmation"
    OWNER = "owner"
    REVIEW = "review"
    KINDS = [
        (REMINDER, "Recordatorio"),
        (REACTIVATION, "Para repetir"),
        (CONFIRMATION, "Confirmación"),
        (OWNER, "Aviso a la dueña"),
        (REVIEW, "Petición de reseña"),
    ]

    SENT = "sent"
    SIMULATED = "simulated"
    FAILED = "failed"
    STATUS = [(SENT, "Enviado"), (SIMULATED, "Simulado (sin Telegram)"), (FAILED, "Error")]

    client = models.ForeignKey("domain.Client", null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=14, choices=KINDS)
    appointment = models.ForeignKey("domain.Appointment", null=True, blank=True, on_delete=models.SET_NULL)
    service = models.ForeignKey("domain.Service", null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS)
    error = models.CharField(max_length=300, blank=True)
    telegram_message_id = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "mensaje enviado"
        verbose_name_plural = "mensajes enviados"
