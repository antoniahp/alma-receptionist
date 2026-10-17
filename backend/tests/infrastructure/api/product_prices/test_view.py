import uuid
from decimal import Decimal

import pytest

from domain.entities.price_offer import PriceOffer

pytestmark = pytest.mark.django_db


def test_owner_compares_prices(owner_client, salon, fake_services):
    fake_services["price_search_service"].offers = [
        PriceOffer(store="Druni", title=salon.oil.name, price=Decimal("9.99"), link="https://t.example")
    ]

    response = owner_client.get(f"/api/products/{salon.oil.id}/prices/")

    assert response.status_code == 200
    assert response.json()["cheapest"]["store"] == "Druni"
    assert response.json()["product"] == salon.oil.name


def test_clients_cannot_use_the_comparator(api_client, salon):
    assert api_client.get(f"/api/products/{salon.oil.id}/prices/").status_code == 401


def test_unknown_product_returns_404(owner_client, salon):
    assert owner_client.get(f"/api/products/{uuid.uuid4()}/prices/").status_code == 404


def test_missing_key_returns_a_clear_error(owner_client, salon, fake_services):
    fake_services["price_search_service"].enabled = False

    response = owner_client.get(f"/api/products/{salon.oil.id}/prices/")

    assert response.status_code == 400
    assert "SERPAPI_API_KEY" in response.json()["detail"]


def test_store_link(owner_client, salon, fake_services):
    fake_services["price_search_service"].links = {"Druni": "https://www.druni.es/aceite"}

    response = owner_client.get("/api/offers/store-link/", {"token": "abc", "store": "Druni"})

    assert response.json() == {"link": "https://www.druni.es/aceite"}
