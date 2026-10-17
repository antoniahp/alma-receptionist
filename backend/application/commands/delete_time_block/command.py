class DeleteTimeBlockCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        block = self.repositories.time_blocks.get(dto.block_id)
        self.repositories.time_blocks.delete(block)
