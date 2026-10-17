from decimal import Decimal

import pytest
from model_bakery import baker

from application.commands.add_to_shopping_list.command import AddToShoppingListCommand
from application.commands.add_to_shopping_list.command_dto import AddToShoppingListCommandDTO
from application.commands.order_from_store.command import OrderFromStoreCommand
from application.commands.order_from_store.command_dto import OrderFromStoreCommandDTO
from domain.entities import PurchaseOrder, ShoppingListItem, Supplier
from domain.exceptions import InvalidShoppingListItem, ShoppingListEmpty
from tests.fakes import FakePriceSearchService

pytestmark = pytest.mark.django_db


def add(repositories, product, store, price, units=1):
    return AddToShoppingListCommand(repositories, FakePriceSearchService()).execute(
        AddToShoppingListCommandDTO(product_id=product.id, store=store, title=product.name, price=Decimal(price), link="", units=units)
    )


def test_the_owner_can_choose_a_more_expensive_offer(repositories, salon):
    add(repositories, salon.oil, "Tienda cara", "30.00", units=2)

    order = OrderFromStoreCommand(repositories).execute(OrderFromStoreCommandDTO(store="Tienda cara", bought_online=True))

    line = order.lines.get()
    assert line.unit_price == Decimal("30.00")
    assert line.units == 2


def test_choosing_the_same_product_again_in_the_same_store_updates_it(repositories, salon):
    add(repositories, salon.oil, "Druni", "10.00")
    add(repositories, salon.oil, "Druni", "9.50", units=3)

    item = ShoppingListItem.objects.get()
    assert item.price == Decimal("9.50")
    assert item.units == 3


def test_bought_online_becomes_an_order_on_its_way_and_creates_the_store_as_supplier(repositories, salon):
    add(repositories, salon.oil, "Druni", "9.50")

    order = OrderFromStoreCommand(repositories).execute(OrderFromStoreCommandDTO(store="Druni", bought_online=True))

    assert order.status == PurchaseOrder.SENT
    assert order.supplier.name == "Druni"
    assert ShoppingListItem.objects.count() == 0


def test_a_store_that_is_our_supplier_gets_an_email_draft(repositories, salon):
    other_product = baker.make("domain.Product", name="Crema", supplier=salon.supplier, unit_price=5, uses_per_unit=1)
    add(repositories, salon.oil, salon.supplier.name, "12.00", units=2)
    add(repositories, other_product, salon.supplier.name, "4.00")

    order = OrderFromStoreCommand(repositories).execute(OrderFromStoreCommandDTO(store=salon.supplier.name, bought_online=False))

    assert order.status == PurchaseOrder.DRAFT
    assert order.supplier == salon.supplier
    assert order.lines.count() == 2
    assert "2 × " + salon.oil.name in order.email_body
    assert Supplier.objects.count() == 1


def test_only_the_items_of_that_store_are_ordered(repositories, salon):
    add(repositories, salon.oil, "Druni", "9.50")
    add(repositories, salon.oil, "Farmacia Imperial", "9.90")

    OrderFromStoreCommand(repositories).execute(OrderFromStoreCommandDTO(store="Druni", bought_online=True))

    assert list(ShoppingListItem.objects.values_list("store", flat=True)) == ["Farmacia Imperial"]


def test_nothing_to_order(repositories, salon):
    with pytest.raises(ShoppingListEmpty):
        OrderFromStoreCommand(repositories).execute(OrderFromStoreCommandDTO(store="Druni", bought_online=True))


def test_zero_units_is_not_allowed(repositories, salon):
    with pytest.raises(InvalidShoppingListItem):
        add(repositories, salon.oil, "Druni", "9.50", units=0)


def test_choosing_an_offer_saves_the_direct_store_link(repositories, salon):
    prices = FakePriceSearchService(links={"Druni": "https://www.druni.es/aceite"})

    item = AddToShoppingListCommand(repositories, prices).execute(
        AddToShoppingListCommandDTO(
            product_id=salon.oil.id,
            store="Druni",
            title="Aceite",
            price=Decimal("9.50"),
            link="https://www.google.com/search?ibp=oshop",
            units=1,
            page_token="token",
        )
    )

    assert item.link == "https://www.druni.es/aceite"


def test_without_direct_link_it_keeps_the_google_one(repositories, salon):
    item = AddToShoppingListCommand(repositories, FakePriceSearchService()).execute(
        AddToShoppingListCommandDTO(
            product_id=salon.oil.id,
            store="Druni",
            title="Aceite",
            price=Decimal("9.50"),
            link="https://www.google.com/x",
            units=1,
            page_token="t",
        )
    )

    assert item.link == "https://www.google.com/x"
