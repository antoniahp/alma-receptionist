import pytest
from model_bakery import baker

from application.commands.discard_order.command import DiscardOrderCommand
from application.commands.discard_order.command_dto import DiscardOrderCommandDTO
from domain.entities import PurchaseOrder
from domain.exceptions import OrderNotDraft

pytestmark = pytest.mark.django_db


def test_discards_draft(repositories, salon):
    order = baker.make(PurchaseOrder, supplier=salon.supplier)

    DiscardOrderCommand(repositories).execute(DiscardOrderCommandDTO(order_id=order.id))

    order.refresh_from_db()
    assert order.status == PurchaseOrder.CANCELLED


def test_cannot_discard_sent_order(repositories, salon):
    order = baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.SENT)

    with pytest.raises(OrderNotDraft):
        DiscardOrderCommand(repositories).execute(DiscardOrderCommandDTO(order_id=order.id))
