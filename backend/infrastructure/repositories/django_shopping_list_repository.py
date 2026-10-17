from domain.entities import ShoppingListItem
from domain.repositories.shopping_list_repository import ShoppingListRepository


class DjangoShoppingListRepository(ShoppingListRepository):
    def list(self):
        return list(ShoppingListItem.objects.select_related("product"))

    def get(self, item_id):
        return ShoppingListItem.objects.select_related("product").get(pk=item_id)

    def add_or_update(self, product, store, title, price, link, units):
        item, _ = ShoppingListItem.objects.update_or_create(
            product=product, store=store, defaults={"title": title, "price": price, "link": link, "units": units}
        )
        return item

    def list_for_store(self, store):
        return list(ShoppingListItem.objects.select_related("product").filter(store=store))

    def save(self, item, fields):
        item.save(update_fields=fields)

    def delete(self, item):
        item.delete()
