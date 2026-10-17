class RemoveFromShoppingListCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        item = self.repositories.shopping_list.get(dto.item_id)
        self.repositories.shopping_list.delete(item)
