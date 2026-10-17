import pytest
from model_bakery import baker

from application.commands.receive_order.command import ReceiveOrderCommand
from application.commands.receive_order.command_dto import ReceiveOrderCommandDTO
from domain.entities import PurchaseOrder, PurchaseOrderLine
from domain.exceptions import OrderNotSent

pytestmark = pytest.mark.django_db


def test_adds_stock_in_uses(repositories, salon):
    order = baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.SENT)
    baker.make(PurchaseOrderLine, order=order, product=salon.oil, units=2, unit_price=15)

    ReceiveOrderCommand(repositories).execute(ReceiveOrderCommandDTO(order_id=order.id))

    salon.oil.refresh_from_db()
    order.refresh_from_db()
    assert salon.oil.stock_uses == 14
    assert order.status == PurchaseOrder.RECEIVED


def test_cannot_receive_a_draft(repositories, salon):
    order = baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.DRAFT)

    with pytest.raises(OrderNotSent):
        ReceiveOrderCommand(repositories).execute(ReceiveOrderCommandDTO(order_id=order.id))
