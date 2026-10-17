from decimal import Decimal

import pytest

from domain.exceptions import PriceSearchUnavailable
from infrastructure.services import serpapi_price_search_service
from infrastructure.services.serpapi_price_search_service import SerpApiPriceSearchService


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


def answer_with(monkeypatch, data):
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse(data)

    monkeypatch.setattr(serpapi_price_search_service.requests, "get", fake_get)
    return calls


def test_reads_google_shopping_results(monkeypatch):
    calls = answer_with(
        monkeypatch,
        {
            "shopping_results": [
                {"title": "OPI GelColor", "source": "Tienda A", "extracted_price": 15.5, "product_link": "https://a.example"},
                {"title": "Sin precio", "source": "Tienda B"},
            ]
        },
    )

    offers = SerpApiPriceSearchService(api_key="clave", country="es").search("OPI GelColor")

    assert calls[0]["engine"] == "google_shopping"
    assert calls[0]["gl"] == "es"
    assert len(offers) == 1
    assert offers[0].store == "Tienda A"
    assert offers[0].price == Decimal("15.50")


def test_no_results_is_an_empty_list(monkeypatch):
    answer_with(monkeypatch, {"error": "Google Shopping hasn't returned any results for this query."})

    assert SerpApiPriceSearchService(api_key="clave").search("producto rarísimo") == []


def test_other_errors_are_reported(monkeypatch):
    answer_with(monkeypatch, {"error": "Invalid API key."})

    with pytest.raises(PriceSearchUnavailable, match="Invalid API key"):
        SerpApiPriceSearchService(api_key="mala").search("OPI")


def test_store_link_finds_the_shop_in_the_product_page(monkeypatch):
    calls = answer_with(
        monkeypatch,
        {
            "product_results": {
                "stores": [
                    {"name": "Amazon.es", "link": "https://www.amazon.es/dp/123"},
                    {"name": "Druni", "link": "https://www.druni.es/cicaplast"},
                ]
            }
        },
    )

    link = SerpApiPriceSearchService(api_key="clave").store_link("token", "Druni")

    assert calls[0]["engine"] == "google_immersive_product"
    assert calls[0]["page_token"] == "token"
    assert link == "https://www.druni.es/cicaplast"


def test_store_link_without_that_shop_is_empty(monkeypatch):
    answer_with(monkeypatch, {"product_results": {"stores": [{"name": "Amazon.es", "link": "https://www.amazon.es/dp/123"}]}})

    assert SerpApiPriceSearchService(api_key="clave").store_link("token", "Druni") == ""
