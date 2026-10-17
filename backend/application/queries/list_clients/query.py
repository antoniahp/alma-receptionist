class ListClientsQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.clients.search(dto.search)
