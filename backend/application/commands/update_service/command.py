from application.commands.create_service.command import FIELDS, check_service_data


class UpdateServiceCommand:
    """Cambia un tratamiento. Las citas ya reservadas mantienen el precio con el que se reservaron."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        check_service_data(dto)
        service = self.repositories.services.get(dto.service_id)
        service.name = dto.name.strip()[:120]
        service.category = dto.category
        service.description = dto.description.strip()
        service.name_en = dto.name_en.strip()[:120]
        service.description_en = dto.description_en.strip()
        service.price = dto.price
        service.duration_minutes = dto.duration_minutes
        service.repeat_every_days = dto.repeat_every_days
        service.active = dto.active
        self.repositories.services.save(service, [*FIELDS, "active"])
        return service
