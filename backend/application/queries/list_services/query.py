class ListServicesQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.services.list(only_active=dto.only_active)
