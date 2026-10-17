from django.db import models

from domain.entities.base_model import BaseModel


class TimeBlock(BaseModel):
    """Horas en las que no se puede reservar (vacaciones, médico, formación...)."""

    start = models.DateTimeField("desde")
    end = models.DateTimeField("hasta")
    reason = models.CharField("motivo", max_length=120, blank=True)

    class Meta:
        ordering = ["start"]
        verbose_name = "bloqueo de agenda"

    def __str__(self):
        return f"{self.start:%d/%m %H:%M} – {self.end:%d/%m %H:%M} {self.reason}"
