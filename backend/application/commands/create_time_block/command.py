from datetime import timedelta

from domain.exceptions import InvalidTimeBlock

LONGEST_BLOCK = timedelta(days=60)


class CreateTimeBlockCommand:
    """Bloquea unas horas de la agenda: ni la web ni Aura ofrecerán huecos ahí."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if dto.end <= dto.start:
            raise InvalidTimeBlock("La hora de fin tiene que ser después de la de inicio.")
        if dto.end - dto.start > LONGEST_BLOCK:
            raise InvalidTimeBlock("Como mucho se pueden bloquear 60 días seguidos.")
        return self.repositories.time_blocks.create(start=dto.start, end=dto.end, reason=dto.reason.strip()[:120])
