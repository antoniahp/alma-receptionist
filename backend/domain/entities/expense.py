from django.db import models

from domain.entities.base_model import BaseModel


class Expense(BaseModel):
    """Un gasto que apunta la dueña (alquiler, luz...). Los pedidos de productos ya cuentan solos."""

    RENT = "alquiler"
    UTILITIES = "suministros"
    SELF_EMPLOYED = "autonomo"
    EQUIPMENT = "material"
    ADVERTISING = "publicidad"
    OTHER = "otros"
    CATEGORIES = [
        (RENT, "Alquiler"),
        (UTILITIES, "Luz, agua e internet"),
        (SELF_EMPLOYED, "Autónomo e impuestos"),
        (EQUIPMENT, "Material y mobiliario"),
        (ADVERTISING, "Publicidad"),
        (OTHER, "Otros"),
    ]

    concept = models.CharField("concepto", max_length=120)
    category = models.CharField("tipo", max_length=20, choices=CATEGORIES, default=OTHER)
    amount = models.DecimalField("importe", max_digits=10, decimal_places=2)
    date = models.DateField("fecha")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name = "gasto"

    def __str__(self):
        return f"{self.concept} · {self.amount} €"
