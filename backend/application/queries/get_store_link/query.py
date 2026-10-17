import hashlib

from django.core.cache import cache

from domain.exceptions import PriceSearchUnavailable
from domain.rules.store_trust import is_trusted_link, is_trusted_store

# Un enlace ya encontrado se recuerda un día: se abre al momento y no gasta otra búsqueda de SerpApi
CACHE_SECONDS = 60 * 60 * 24


class GetStoreLinkQuery:
    """Enlace directo a la tienda para una oferta del comparador ('' si no se encuentra).

    Si la tienda es de confianza, el enlace tiene que estar en su dominio; si no, se descarta por seguridad.
    """

    def __init__(self, price_search_service, repositories):
        self.price_search_service = price_search_service
        self.repositories = repositories

    def execute(self, dto):
        if not self.price_search_service.is_enabled():
            raise PriceSearchUnavailable("El comparador no está configurado: falta SERPAPI_API_KEY en backend/.env.")
        key = "store-link:" + hashlib.sha256(f"{dto.page_token}|{dto.store}".encode()).hexdigest()
        link = cache.get(key)
        if link is None:
            link = self.price_search_service.store_link(dto.page_token, dto.store)
            cache.set(key, link, CACHE_SECONDS)
        suppliers = self.repositories.suppliers.list()
        if link and is_trusted_store(dto.store, suppliers) and not is_trusted_link(dto.store, link, suppliers):
            return ""
        if link and not link.startswith("https://"):
            return ""
        return link
