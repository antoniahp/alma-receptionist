from decimal import Decimal

from domain.rules.price_matching import supplier_for_store
from domain.rules.store_trust import amazon_cart_link, is_trusted_store, known_store


class GetShoppingListQuery:
    """La lista de compra agrupada por tienda, indicando si la tienda es uno de nuestros proveedores."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        suppliers = self.repositories.suppliers.list()
        groups = {}
        for item in self.repositories.shopping_list.list():
            if item.store not in groups:
                supplier = supplier_for_store(suppliers, item.store)
                groups[item.store] = {"store": item.store, "supplier": supplier, "items": [], "total": Decimal("0")}
            groups[item.store]["items"].append(item)
            groups[item.store]["total"] += item.total
        for group in groups.values():
            group["cart_link"] = self.cart_link(group)
            group["trusted"] = is_trusted_store(group["store"], suppliers)
        return list(groups.values())

    def cart_link(self, group):
        """Amazon permite meter varios productos en el carrito con un solo enlace. Las demás tiendas, no."""
        if known_store(group["store"]) != "amazon":
            return ""
        return amazon_cart_link([(item.link, item.units) for item in group["items"]])
