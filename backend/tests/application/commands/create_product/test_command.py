from decimal import Decimal

import pytest

from application.commands.count_stock.command import CountStockCommand
from application.commands.count_stock.command_dto import CountStockCommandDTO
from application.commands.create_product.command import CreateProductCommand
from application.commands.create_product.command_dto import CreateProductCommandDTO
from domain.entities import ServiceProduct, StockMovement, Supplier
from domain.exceptions import InvalidProductData

pytestmark = pytest.mark.django_db


def test_owner_adds_wax_strips_with_a_new_supplier(repositories, salon):
    product = CreateProductCommand(repositories).execute(
        CreateProductCommandDTO(
            name="Bandas de depilación (paquete de 100)",
            unit_price=Decimal("4.50"),
            uses_per_unit=20,
            units_in_stock=3,
            min_units=1,
            new_supplier_name="Starpil",
            service_ids=[salon.massage.id],
        )
    )

    assert product.stock_uses == 60
    assert product.min_uses == 20
    assert Supplier.objects.filter(name="Starpil").exists()
    assert ServiceProduct.objects.filter(service=salon.massage, product=product, uses=1).exists()


def test_a_supplier_is_needed(repositories, salon):
    with pytest.raises(InvalidProductData):
        CreateProductCommand(repositories).execute(
            CreateProductCommandDTO(name="Bandas", unit_price=Decimal("1"), uses_per_unit=1, units_in_stock=1, min_units=0)
        )


def test_count_stock_records_the_difference(repositories, salon):
    salon.oil.refresh_from_db()
    before = salon.oil.stock_uses

    product = CountStockCommand(repositories).execute(CountStockCommandDTO(product_id=salon.oil.id, uses_in_stock=before + 3))

    assert product.stock_uses == before + 3
    assert StockMovement.objects.filter(product=salon.oil, change=3, reason="Recuento a mano").exists()
