from django.db import models

from domain.entities.base_model import BaseModel


class Supplier(BaseModel):
    name = models.CharField("nombre", max_length=120)
    contact_name = models.CharField("persona de contacto", max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.name
