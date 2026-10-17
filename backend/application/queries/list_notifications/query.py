class ListNotificationsQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.notifications.list_recent(dto.limit)
