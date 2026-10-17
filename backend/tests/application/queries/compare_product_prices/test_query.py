from decimal import Decimal

import pytest

from application.queries.compare_product_prices.query import CompareProductPricesQuery
from application.queries.compare_product_prices.query_dto import CompareProductPricesQueryDTO
from domain.entities.price_offer import PriceOffer
from domain.exceptions import PriceSearchUnavailable
from tests.fakes import FakePriceSearchService

pytestmark = pytest.mark.django_db


def offer(store, price, title=None):
    return PriceOffer(store=store, title=title or "Aceite de almendras 500 ml", price=Decimal(price), link=f"https://{store}.example/p")


def test_offers_are_sorted_and_saving_is_calculated(repositories, salon):
    salon.oil.unit_price = Decimal("14.90")
    salon.oil.save()
    prices = FakePriceSearchService(offers=[offer("Primor", "13.50"), offer("Druni", "12.00"), offer("Notino", "16.00")])

    result = CompareProductPricesQuery(repositories, prices).execute(CompareProductPricesQueryDTO(product_id=salon.oil.id))

    assert prices.queries == [salon.oil.name]
    assert [o.store for o in result["offers"]] == ["Druni", "Primor", "Notino"]
    assert result["cheapest"].store == "Druni"
    assert result["saving"] == Decimal("2.90")


def test_no_saving_when_we_already_pay_less(repositories, salon):
    salon.oil.unit_price = Decimal("10.00")
    salon.oil.save()
    prices = FakePriceSearchService(offers=[offer("tienda-a", "12.00")])

    result = CompareProductPricesQuery(repositories, prices).execute(CompareProductPricesQueryDTO(product_id=salon.oil.id))

    assert result["saving"] is None


def test_without_api_key_it_explains_what_is_missing(repositories, salon):
    with pytest.raises(PriceSearchUnavailable, match="SERPAPI_API_KEY"):
        CompareProductPricesQuery(repositories, FakePriceSearchService(enabled=False)).execute(
            CompareProductPricesQueryDTO(product_id=salon.oil.id)
        )


def test_offers_of_other_products_are_left_out(repositories, salon):
    prices = FakePriceSearchService(offers=[offer("tienda-a", "1.79", title="Ziaja crema contorno de ojos"), offer("tienda-b", "13.00")])

    result = CompareProductPricesQuery(repositories, prices).execute(CompareProductPricesQueryDTO(product_id=salon.oil.id))

    assert [o.store for o in result["offers"]] == ["tienda-b"]
    assert result["discarded"] == 1


def test_unknown_shops_go_last_and_do_not_count_as_cheapest(repositories, salon):
    prices = FakePriceSearchService(offers=[offer("Estéticas Pasco", "5.00"), offer("Druni", "12.00")])

    result = CompareProductPricesQuery(repositories, prices).execute(CompareProductPricesQueryDTO(product_id=salon.oil.id))

    assert [(o.store, o.trusted) for o in result["offers"]] == [("Druni", True), ("Estéticas Pasco", False)]
    assert result["cheapest"].store == "Druni"
    assert result["unverified"] == 1
