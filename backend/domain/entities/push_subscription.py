from django.db import models

from domain.entities.base_model import BaseModel


class PushSubscription(BaseModel):
    """Un navegador de la dueña que ha aceptado recibir avisos (Web Push), aunque tenga el panel cerrado."""

    endpoint = models.URLField(max_length=600, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "aviso del navegador"

    def __str__(self):
        return self.endpoint[:60]
