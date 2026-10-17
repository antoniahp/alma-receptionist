from django.conf import settings

from application.queries.get_opening_hours_text.query import GetOpeningHoursTextQuery
from application.queries.get_opening_hours_text.query_dto import GetOpeningHoursTextQueryDTO
from domain.entities import Service


class GetPublicInfoQuery:
    """Datos que ve cualquiera en la página de reservas."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        business = settings.BUSINESS
        services = self.repositories.services.list(only_active=True)
        categories = []
        for key, label in Service.CATEGORIES:
            if any(service.category == key for service in services):
                categories.append({"key": key, "label": label})
        return {
            "name": business["name"],
            "address": business["address"],
            "phone": business["phone"],
            "owner": business["owner"],
            "assistant_name": business["assistant_name"],
            "legal_name": business["legal_name"],
            "nif": business["nif"],
            "email": business["email"],
            "hours": GetOpeningHoursTextQuery(self.repositories).execute(GetOpeningHoursTextQueryDTO()),
            "telegram_bot": settings.TELEGRAM_BOT_USERNAME,
            # Solo en la demo pública: el usuario de prueba se enseña en la pantalla de entrada
            "demo_login": {"username": settings.DEMO_USERNAME, "password": settings.DEMO_PASSWORD} if settings.DEMO_MODE and settings.DEMO_HINTS else None,
            "categories": categories,
            "services": services,
        }
