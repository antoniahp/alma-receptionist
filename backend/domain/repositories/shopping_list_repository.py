from abc import ABC, abstractmethod


class ShoppingListRepository(ABC):
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def get(self, item_id):
        """Devuelve el elemento o lanza ShoppingListItem.DoesNotExist."""

    @abstractmethod
    def add_or_update(self, product, store, title, price, link, units):
        """Si ese producto ya estaba en la lista para esa tienda, se actualiza."""

    @abstractmethod
    def list_for_store(self, store):
        pass

    @abstractmethod
    def save(self, item, fields):
        pass

    @abstractmethod
    def delete(self, item):
        pass
