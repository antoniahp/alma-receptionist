from domain.entities import Service
from domain.exceptions import InvalidServiceData

FIELDS = ["name", "category", "description", "name_en", "description_en", "price", "duration_minutes", "repeat_every_days"]


def check_service_data(dto):
    """Reglas comunes al crear y al editar un tratamiento."""
    if len(dto.name.strip()) < 3:
        raise InvalidServiceData("Ponle un nombre al tratamiento.")
    if dto.category not in dict(Service.CATEGORIES):
        raise InvalidServiceData("Elige una categoría.")
    if dto.price < 0 or dto.price > 2000:
        raise InvalidServiceData("Revisa el precio.")
    if dto.duration_minutes < 10 or dto.duration_minutes > 480:
        raise InvalidServiceData("La duración tiene que estar entre 10 minutos y 8 horas.")
    if dto.repeat_every_days is not None and not 1 <= dto.repeat_every_days <= 365:
        raise InvalidServiceData("Cada cuántos días se repite: entre 1 y 365, o déjalo vacío.")


class CreateServiceCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        check_service_data(dto)
        return self.repositories.services.create(
            name=dto.name.strip()[:120],
            category=dto.category,
            description=dto.description.strip(),
            name_en=dto.name_en.strip()[:120],
            description_en=dto.description_en.strip(),
            price=dto.price,
            duration_minutes=dto.duration_minutes,
            repeat_every_days=dto.repeat_every_days,
        )
