from django.db import models

from domain.entities.base_model import BaseModel


class Service(BaseModel):
    FACIAL = "facial"
    HANDS_FEET = "manos_pies"
    WAXING = "depilacion"
    BROWS_LASHES = "cejas_pestanas"
    MAKEUP = "maquillaje"
    # El orden de esta lista es el orden en la web y en el chat
    CATEGORIES = [
        (FACIAL, "Facial"),
        (HANDS_FEET, "Manos y pies"),
        (WAXING, "Depilación"),
        (BROWS_LASHES, "Cejas y pestañas"),
        (MAKEUP, "Maquillaje"),
    ]
    CATEGORY_LABELS_EN = {
        FACIAL: "Facial",
        HANDS_FEET: "Hands & feet",
        WAXING: "Waxing",
        BROWS_LASHES: "Brows & lashes",
        MAKEUP: "Make-up",
    }

    name = models.CharField("nombre", max_length=120)
    category = models.CharField("categoría", max_length=20, choices=CATEGORIES, default=FACIAL)
    description = models.TextField("descripción", blank=True, help_text="La recepcionista la usa para recomendar")
    # Para la web en inglés. Si están vacíos se usa el texto en español.
    name_en = models.CharField("nombre en inglés", max_length=120, blank=True)
    description_en = models.TextField("descripción en inglés", blank=True)
    keywords = models.CharField(
        "palabras clave", max_length=200, blank=True, help_text="Separadas por comas, para entender a qué servicio se refiere la clienta"
    )
    duration_minutes = models.PositiveIntegerField("duración (min)", default=60)
    price = models.DecimalField("precio", max_digits=8, decimal_places=2)
    repeat_every_days = models.PositiveIntegerField("repetir cada (días)", null=True, blank=True)
    active = models.BooleanField(default=True)
    products = models.ManyToManyField("domain.Product", through="domain.ServiceProduct", related_name="services", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "servicio"

    def __str__(self):
        return self.name

    def keyword_list(self):
        words = [word.strip() for word in self.keywords.split(",") if word.strip()]
        # El nombre en inglés también sirve para entender a quien escribe en inglés
        return words + [self.name] + ([self.name_en] if self.name_en else [])


class ServiceProduct(BaseModel):
    """Cuántos usos de un producto gasta cada servicio."""

    service = models.ForeignKey("domain.Service", on_delete=models.CASCADE, related_name="consumption")
    product = models.ForeignKey("domain.Product", on_delete=models.CASCADE, related_name="consumption")
    uses = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["service", "product"], name="unique_service_product")]
