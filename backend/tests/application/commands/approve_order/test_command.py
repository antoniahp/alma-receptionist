import pytest
from model_bakery import baker

from application.commands.approve_order.command import ApproveOrderCommand
from application.commands.approve_order.command_dto import ApproveOrderCommandDTO
from domain.entities import PurchaseOrder
from domain.exceptions import OrderNotDraft

pytestmark = pytest.mark.django_db


def test_sends_email_and_marks_as_sent(repositories, salon, email_service):
    order = baker.make(PurchaseOrder, supplier=salon.supplier, email_subject="Pedido", email_body="Hola")

    ApproveOrderCommand(repositories, email_service).execute(ApproveOrderCommandDTO(order_id=order.id))

    order.refresh_from_db()
    assert order.status == PurchaseOrder.SENT
    assert email_service.sent == [{"to": "pedidos@aromas.example", "subject": "Pedido", "body": "Hola"}]


def test_cannot_approve_twice(repositories, salon, email_service):
    order = baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.SENT)

    with pytest.raises(OrderNotDraft):
        ApproveOrderCommand(repositories, email_service).execute(ApproveOrderCommandDTO(order_id=order.id))
