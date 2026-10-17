from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.utils import timezone
from model_bakery import baker

from application.queries.get_finances.query import GetFinancesQuery
from application.queries.get_finances.query_dto import GetFinancesQueryDTO
from domain.entities import Appointment, Expense, PurchaseOrder, PurchaseOrderLine

pytestmark = pytest.mark.django_db

MARCH = date(2026, 3, 1)


def at(day, hour=11):
    return timezone.make_aware(datetime.combine(day, time(hour)))


def completed(salon, day, price):
    return baker.make(
        Appointment, client=salon.laura, service=salon.massage, start=at(day), status=Appointment.COMPLETED, price=Decimal(price)
    )


def test_income_spending_and_profit_of_a_month(repositories, salon):
    completed(salon, date(2026, 3, 2), "45")
    completed(salon, date(2026, 3, 31), "40")
    completed(salon, date(2026, 4, 1), "999")  # otro mes: no cuenta
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=at(date(2026, 3, 5)), status=Appointment.CANCELLED, price=50)
    order = baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.RECEIVED, sent_at=at(date(2026, 3, 10)))
    baker.make(PurchaseOrderLine, order=order, product=salon.oil, units=2, unit_price=Decimal("14.90"))
    baker.make(PurchaseOrder, supplier=salon.supplier, status=PurchaseOrder.DRAFT)  # borrador: aún no es gasto
    baker.make(Expense, concept="Alquiler", category=Expense.RENT, amount=Decimal("650"), date=date(2026, 3, 1))
    baker.make(Expense, concept="Luz", category=Expense.UTILITIES, amount=Decimal("80.50"), date=date(2026, 3, 15))

    result = GetFinancesQuery(repositories).execute(GetFinancesQueryDTO(month=date(2026, 3, 20)))

    assert result["month"] == MARCH
    assert result["income"] == Decimal("85")
    assert result["appointments_completed"] == 2
    assert result["product_spending"] == Decimal("29.80")
    assert result["other_spending"] == Decimal("730.50")
    assert result["spending"] == Decimal("760.30")
    assert result["profit"] == Decimal("-675.30")
    assert result["spending_by_category"][0] == {"label": "Alquiler", "amount": Decimal("650")}


def test_the_price_of_the_day_of_the_booking_is_kept(repositories, salon):
    completed(salon, date(2026, 3, 2), "45")
    salon.massage.price = Decimal("60")
    salon.massage.save()

    result = GetFinancesQuery(repositories).execute(GetFinancesQueryDTO(month=MARCH))

    assert result["income"] == Decimal("45")


def test_history_has_the_last_months_oldest_first(repositories, salon):
    completed(salon, date(2026, 1, 10), "30")

    result = GetFinancesQuery(repositories).execute(GetFinancesQueryDTO(month=MARCH, months_of_history=3))

    assert [item["month"] for item in result["history"]] == [date(2026, 1, 1), date(2026, 2, 1), MARCH]
    assert result["history"][0]["income"] == Decimal("30")


def test_income_by_category(repositories, salon):
    completed(salon, date(2026, 3, 2), "45")
    completed(salon, date(2026, 3, 3), "45")

    result = GetFinancesQuery(repositories).execute(GetFinancesQueryDTO(month=MARCH))

    assert result["income_by_category"] == [{"label": "Facial", "amount": Decimal("90"), "count": 2}]


def test_packs_count_when_sold_and_not_again_when_used(repositories, salon):
    pack = baker.make(
        "domain.ClientPack",
        client=salon.laura,
        service=salon.massage,
        sessions_total=5,
        price=Decimal("200"),
        payment_method="tarjeta",
        sold_at=at(date(2026, 3, 3)),
    )
    baker.make(
        Appointment,
        client=salon.laura,
        service=salon.massage,
        start=at(date(2026, 3, 10)),
        status=Appointment.COMPLETED,
        price=Decimal("45"),
        payment_method="bono",
        pack=pack,
    )

    result = GetFinancesQuery(repositories).execute(GetFinancesQueryDTO(month=MARCH))

    assert result["income"] == Decimal("200")
    assert {"label": "Bonos", "amount": Decimal("200"), "count": 1} in result["income_by_category"]
