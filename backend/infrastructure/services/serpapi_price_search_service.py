"""Busca precios en Google Shopping a través de SerpApi (https://serpapi.com/google-shopping-api)."""

from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings

from domain.entities.price_offer import PriceOffer
from domain.exceptions import PriceSearchUnavailable
from domain.rules.text_normalizer import normalize_text
from domain.services.price_search_service import PriceSearchService

SEARCH_URL = "https://serpapi.com/search.json"


class SerpApiPriceSearchService(PriceSearchService):
    def __init__(self, api_key=None, country=None):
        self.api_key = api_key if api_key is not None else settings.SERPAPI_API_KEY
        self.country = country or settings.SERPAPI_COUNTRY

    def is_enabled(self):
        return bool(self.api_key)

    def ask(self, params):
        try:
            response = requests.get(SEARCH_URL, params={**params, "api_key": self.api_key}, timeout=20)
            return response.json()
        except (requests.RequestException, ValueError) as error:
            raise PriceSearchUnavailable() from error

    def search(self, query):
        data = self.ask({"engine": "google_shopping", "q": query, "gl": self.country, "hl": "es"})
        if "error" in data:
            # Sin resultados no es un fallo: simplemente no hay ofertas
            if "hasn't returned any results" in data["error"]:
                return []
            raise PriceSearchUnavailable(f"SerpApi: {data['error']}")

        offers = []
        for result in data.get("shopping_results", []):
            price = self.read_price(result.get("extracted_price"))
            if price is None:
                continue
            offers.append(
                PriceOffer(
                    store=result.get("source", "Tienda"),
                    title=result.get("title", ""),
                    price=price,
                    # Esto es la ficha de Google Shopping; el enlace de la tienda se pide con store_link
                    link=result.get("product_link") or "",
                    page_token=result.get("immersive_product_page_token", ""),
                )
            )
        return offers

    def store_link(self, page_token, store):
        """Google Immersive Product: lista las tiendas que venden el producto con su enlace directo."""
        if not page_token:
            return ""
        data = self.ask(
            {"engine": "google_immersive_product", "page_token": page_token, "more_stores": "true", "hl": "es", "gl": self.country}
        )
        if "error" in data:
            raise PriceSearchUnavailable(f"SerpApi: {data['error']}")
        wanted = normalize_text(store)
        for shop in data.get("product_results", {}).get("stores", []):
            name = normalize_text(shop.get("name", ""))
            if name and (name in wanted or wanted in name) and shop.get("link"):
                return shop["link"]
        return ""

    def read_price(self, value):
        if value is None:
            return None
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except InvalidOperation:
            return None
