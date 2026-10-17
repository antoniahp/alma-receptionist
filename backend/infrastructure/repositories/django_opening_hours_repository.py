from domain.entities import OpeningHours
from domain.repositories.opening_hours_repository import OpeningHoursRepository


class DjangoOpeningHoursRepository(OpeningHoursRepository):
    def list_all(self):
        return list(OpeningHours.objects.all())

    def list_for_weekday(self, weekday):
        return list(OpeningHours.objects.filter(weekday=weekday))

    def lock_weekday(self, weekday):
        list(OpeningHours.objects.select_for_update().filter(weekday=weekday))

    def is_open(self, weekday):
        return OpeningHours.objects.filter(weekday=weekday).exists()
