from dataclasses import replace

from domain.exceptions import PriceSearchUnavailable
from domain.rules.price_matching import is_same_product, is_second_hand
from domain.rules.store_trust import is_trusted_store

MAX_OFFERS = 8


class CompareProductPricesQuery:
    """Compara lo que pagamos por un producto con lo que piden las tiendas online."""

    def __init__(self, repositories, price_search_service):
        self.repositories = repositories
        self.price_search_service = price_search_service

    def execute(self, dto):
        product = self.repositories.products.get(dto.product_id)
        if not self.price_search_service.is_enabled():
            raise PriceSearchUnavailable("El comparador no está configurado: falta SERPAPI_API_KEY en backend/.env.")

        found = self.price_search_service.search(product.name)
        # Solo cuentan las ofertas del mismo producto: una crema de otra marca no es "más barata", es otra cosa
        matching = [offer for offer in found if is_same_product(product.name, offer.title) and not is_second_hand(offer.store)]
        suppliers = self.repositories.suppliers.list()
        matching = [replace(offer, trusted=is_trusted_store(offer.store, suppliers)) for offer in matching]
        trusted = sorted([offer for offer in matching if offer.trusted], key=lambda offer: offer.price)[:MAX_OFFERS]
        unverified = sorted([offer for offer in matching if not offer.trusted], key=lambda offer: offer.price)[:MAX_OFFERS]
        offers = trusted + unverified
        # El ahorro solo se calcula con tiendas de confianza
        cheapest = trusted[0] if trusted else None
        saving = None
        if cheapest and cheapest.price < product.unit_price:
            saving = product.unit_price - cheapest.price
        return {
            "product": product,
            "our_price": product.unit_price,
            "offers": offers,
            "cheapest": cheapest,
            "saving": saving,
            "discarded": len(found) - len(matching),
            "unverified": len(unverified),
        }
