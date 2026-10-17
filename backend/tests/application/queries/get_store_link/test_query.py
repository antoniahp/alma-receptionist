import pytest

from application.queries.get_store_link.query import GetStoreLinkQuery
from application.queries.get_store_link.query_dto import GetStoreLinkQueryDTO
from tests.fakes import FakePriceSearchService

pytestmark = pytest.mark.django_db


def test_the_second_time_the_link_comes_from_memory(repositories):
    prices = FakePriceSearchService(links={"Druni": "https://www.druni.es/a"})
    calls = []
    real_store_link = prices.store_link

    def counting_store_link(page_token, store):
        calls.append(store)
        return real_store_link(page_token, store)

    prices.store_link = counting_store_link
    query = GetStoreLinkQuery(prices, repositories)

    first = query.execute(GetStoreLinkQueryDTO(page_token="t", store="Druni"))
    second = query.execute(GetStoreLinkQueryDTO(page_token="t", store="Druni"))

    assert first == second == "https://www.druni.es/a"
    assert calls == ["Druni"]


def test_a_link_outside_the_store_domain_is_rejected(repositories):
    prices = FakePriceSearchService(links={"Druni": "https://druni-ofertas.example/crema"})

    link = GetStoreLinkQuery(prices, repositories).execute(GetStoreLinkQueryDTO(page_token="t", store="Druni"))

    assert link == ""
