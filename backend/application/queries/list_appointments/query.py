from datetime import timedelta

from application.shared.schedule import start_of_day


class ListAppointmentsQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        start = start_of_day(dto.date_from) if dto.date_from else None
        end = start_of_day(dto.date_to) + timedelta(days=1) if dto.date_to else None
        return self.repositories.appointments.list_between(start, end, dto.statuses)
