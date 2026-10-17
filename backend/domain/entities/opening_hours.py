from django.db import models

from domain.entities.base_model import BaseModel


class OpeningHours(BaseModel):
    WEEKDAYS = [(0, "Lunes"), (1, "Martes"), (2, "Miércoles"), (3, "Jueves"), (4, "Viernes"), (5, "Sábado"), (6, "Domingo")]

    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    opens = models.TimeField()
    closes = models.TimeField()

    class Meta:
        ordering = ["weekday", "opens"]
        verbose_name = "horario"
        verbose_name_plural = "horarios"

    def __str__(self):
        return f"{self.get_weekday_display()} {self.opens:%H:%M}-{self.closes:%H:%M}"
