from domain.rules import customer_messages


class GetOpeningHoursTextQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return customer_messages.hours_text(self.repositories.opening_hours.list_all())
