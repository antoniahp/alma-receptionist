from datetime import time
from decimal import Decimal
from types import SimpleNamespace

from domain.rules import customer_messages


def hours(weekday, opens, closes):
    return SimpleNamespace(weekday=weekday, opens=time(opens), closes=time(closes))


def test_hours_text_groups_days_with_same_schedule():
    opening = []
    for weekday in range(6):
        opening += [hours(weekday, 10, 14), hours(weekday, 16, 20)]

    text = customer_messages.hours_text(opening)

    assert text == "Abrimos de lunes a sábado, de 10:00 a 14:00 y de 16:00 a 20:00. Los domingos cerramos."


def test_hours_text_without_schedule():
    assert "no tengo el horario" in customer_messages.hours_text([])


def test_offer_slots_intro_only_says_the_price_if_asked():
    service = SimpleNamespace(name="Limpieza facial", price=Decimal("40.00"), duration_minutes=60)

    assert "€" not in customer_messages.offer_slots_intro(service)
    assert "40\u00a0€" in customer_messages.offer_slots_intro(service, with_price=True)


def test_offer_slots_intro_always_names_the_treatment():
    service = SimpleNamespace(name="Masaje facial", price=Decimal("20.00"), duration_minutes=20)

    for _ in range(10):
        assert "masaje facial" in customer_messages.offer_slots_intro(service)


def test_service_info_does_not_say_the_price():
    service = SimpleNamespace(name="Masaje facial", description="Cara, cuello y escote.", price=Decimal("20.00"), duration_minutes=20)

    text = customer_messages.service_info(service)

    assert "masaje facial" in text
    assert "€" not in text
