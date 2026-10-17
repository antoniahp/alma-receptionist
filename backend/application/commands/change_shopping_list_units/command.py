from domain.exceptions import InvalidShoppingListItem


class ChangeShoppingListUnitsCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if dto.units < 1:
            raise InvalidShoppingListItem("Tiene que ser al menos una unidad. Si no lo quieres, quítalo de la lista.")
        item = self.repositories.shopping_list.get(dto.item_id)
        item.units = dto.units
        self.repositories.shopping_list.save(item, ["units"])
        return item
