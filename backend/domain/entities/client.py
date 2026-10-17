import secrets

from django.db import models

from domain.entities.base_model import BaseModel


def new_link_code():
    return secrets.token_urlsafe(8)


class Client(BaseModel):
    name = models.CharField("nombre", max_length=120)
    phone = models.CharField("teléfono", max_length=30, blank=True)
    email = models.EmailField(blank=True)
    telegram_chat_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    telegram_link_code = models.CharField(max_length=20, unique=True, default=new_link_code)
    accepts_reminders = models.BooleanField("acepta mensajes para repetir", default=True)
    notes = models.TextField("notas", blank=True)
    # Protección de datos: cuándo aceptó la política de privacidad
    privacy_accepted_at = models.DateTimeField(null=True, blank=True)
    # Ya se le pidió una reseña en Google (solo una vez)
    review_requested_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "clienta"

    def __str__(self):
        return self.name

    @property
    def first_name(self):
        return self.name.split(" ")[0] if self.name else ""

    @property
    def has_telegram(self):
        return bool(self.telegram_chat_id)
