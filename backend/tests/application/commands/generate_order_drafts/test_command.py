import pytest

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.commands.generate_order_drafts.command import GenerateOrderDraftsCommand
from application.commands.generate_order_drafts.command_dto import GenerateOrderDraftsCommandDTO
from domain.entities import PurchaseOrder
from tests.fakes import FakeLanguageModelService
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


@pytest.fixture
def oil_runs_low(repositories, salon, next_monday, message_service):
    for hour in (10, 11, 12):
        BookAppointmentCommand(repositories, message_service).execute(
            BookAppointmentCommandDTO(
                client_id=salon.laura.id, service_id=salon.massage.id, start=local_datetime(next_monday, hour), source="owner"
            )
        )


def test_creates_one_draft_per_supplier_with_template(repositories, salon, oil_runs_low, language_model_service):
    drafts = GenerateOrderDraftsCommand(repositories, language_model_service).execute(GenerateOrderDraftsCommandDTO())

    order = drafts[0]
    assert order.status == PurchaseOrder.DRAFT
    assert order.written_by_ai is False
    assert order.lines.get().units == 2
    assert "2 × Aceite de almendras" in order.email_body


def test_running_twice_does_not_duplicate_drafts(repositories, salon, oil_runs_low, language_model_service):
    command = GenerateOrderDraftsCommand(repositories, language_model_service)
    command.execute(GenerateOrderDraftsCommandDTO())
    command.execute(GenerateOrderDraftsCommandDTO())

    assert PurchaseOrder.objects.count() == 1


def test_uses_ai_email_when_it_contains_every_line(repositories, salon, oil_runs_low):
    model = FakeLanguageModelService(
        json_response={"subject": "Pedido", "body": "Hola Pilar, queremos 2 unidades de Aceite de almendras. Gracias."}
    )

    order = GenerateOrderDraftsCommand(repositories, model).execute(GenerateOrderDraftsCommandDTO())[0]

    assert order.written_by_ai is True
    assert order.email_subject == "Pedido"


def test_falls_back_to_template_if_ai_forgets_a_line(repositories, salon, oil_runs_low):
    model = FakeLanguageModelService(json_response={"subject": "Pedido", "body": "Hola Pilar, queremos aceite."})

    order = GenerateOrderDraftsCommand(repositories, model).execute(GenerateOrderDraftsCommandDTO())[0]

    assert order.written_by_ai is False
    assert "2 × Aceite de almendras" in order.email_body


def test_nothing_to_order(repositories, salon, language_model_service):
    assert GenerateOrderDraftsCommand(repositories, language_model_service).execute(GenerateOrderDraftsCommandDTO()) == []
