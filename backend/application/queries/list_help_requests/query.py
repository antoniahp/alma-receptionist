class ListHelpRequestsQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.help_requests.list(dto.statuses, dto.limit)
