from domain.entities import TimeBlock
from domain.repositories.time_block_repository import TimeBlockRepository


class DjangoTimeBlockRepository(TimeBlockRepository):
    def create(self, start, end, reason):
        return TimeBlock.objects.create(start=start, end=end, reason=reason)

    def get(self, block_id):
        return TimeBlock.objects.get(pk=block_id)

    def delete(self, block):
        block.delete()

    def list_overlapping(self, start, end):
        return list(TimeBlock.objects.filter(start__lt=end, end__gt=start))
