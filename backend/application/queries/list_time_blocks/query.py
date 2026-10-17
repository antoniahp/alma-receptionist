class ListTimeBlocksQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.time_blocks.list_overlapping(dto.start, dto.end)
