from abc import ABC, abstractmethod


class PriceSearchService(ABC):
    @abstractmethod
    def is_enabled(self):
        """True si está configurado (tiene clave)."""

    @abstractmethod
    def search(self, query):
        """Lista de PriceOffer para ese producto. Lanza PriceSearchUnavailable si falla."""

    @abstractmethod
    def store_link(self, page_token, store):
        """Enlace directo a la página del producto en esa tienda, o '' si no se encuentra."""
