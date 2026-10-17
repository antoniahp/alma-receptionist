from datetime import date

import pytest

from domain.rules import intent_detector as intents

MONDAY = date(2030, 1, 7)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("¿Eres un bot?", intents.ASK_IF_BOT),
        ("Quiero hablar con Cris", intents.TALK_TO_OWNER),
        ("Estoy embarazada, ¿puedo hacerme un masaje?", intents.HEALTH_QUESTION),
        ("Tengo que cancelar mi cita", intents.CHANGE_APPOINTMENT),
        ("Quiero pedir cita", intents.BOOK),
        ("¿Cuánto cuesta?", intents.PRICES),
        ("¿Qué horario tenéis?", intents.HOURS),
        ("Tengo la piel muy seca", intents.RECOMMEND),
        ("Gracias!", intents.THANKS),
        ("Hola", intents.GREETING),
        ("¿Hacéis micropigmentación?", intents.UNKNOWN),
    ],
)
def test_detect_intent(text, expected):
    assert intents.detect_intent(text, "Cris", mentions_service=False, mentions_day=False) == expected


def test_greeting_with_question_is_not_just_a_greeting():
    assert intents.detect_intent("Hola, ¿hacéis láser?", "Cris", False, False) == intents.UNKNOWN


def test_service_and_day_means_booking():
    assert intents.detect_intent("masaje el viernes", "Cris", mentions_service=True, mentions_day=True) == intents.BOOK


@pytest.mark.parametrize(
    "text, expected",
    [
        ("mañana", date(2030, 1, 8)),
        ("pasado mañana", date(2030, 1, 9)),
        ("hoy", MONDAY),
        ("el viernes", date(2030, 1, 11)),
        ("el lunes", date(2030, 1, 14)),
    ],
)
def test_parse_day(text, expected):
    assert intents.parse_day(text, MONDAY) == expected


def test_por_la_manana_is_not_tomorrow():
    assert intents.parse_day("el jueves por la mañana", MONDAY) == date(2030, 1, 10)
    assert intents.parse_part_of_day("el jueves por la mañana") == "morning"


def test_extract_phone():
    assert intents.extract_phone("Claro, es el 612 345 678") == "612345678"
    assert intents.extract_phone("no gracias") is None


def test_clean_name():
    assert intents.clean_name("me llamo marta ruiz") == "Marta Ruiz"
    assert intents.clean_name("esto es una frase demasiado larga para un nombre") is None


def test_mentions_owner_handoff():
    assert intents.mentions_owner_handoff("Se lo pregunto a Cris y te digo", "Cris")
    assert not intents.mentions_owner_handoff("Cris es muy maja", "Cris")


def test_claims_false_action():
    assert intents.claims_false_action("¡Listo! Te he reservado el masaje")
    assert not intents.claims_false_action("¿Te reservo el masaje?")


def test_asks_price():
    assert intents.asks_price("¿Cuánto cuesta la limpieza facial y tenéis hueco mañana?")
    assert intents.asks_price("qué precio tiene")
    assert not intents.asks_price("¿Hacéis masajes?")
    assert not intents.asks_price("Vale, quiero cita")


def test_greeting_with_a_question_about_a_treatment_is_not_just_a_greeting():
    assert intents.detect_intent("hola haces masaje", "Cris", mentions_service=True, mentions_day=False) == intents.SERVICE_INFO
    assert intents.detect_intent("hola", "Cris", mentions_service=False, mentions_day=False) == intents.GREETING


def test_wanting_a_treatment_is_booking():
    assert intents.detect_intent("quiero un masaje", "Cris", mentions_service=True, mentions_day=False) == intents.BOOK


def test_a_phone_number_is_not_a_name():
    assert intents.clean_name("611 111 111") is None
    assert intents.clean_name("Me llamo Marta Ruiz") == "Marta Ruiz"


@pytest.mark.parametrize("text,expected", [
    ("Do you have an appointment to get your eyebrows waxed tomorrow?", "cejas_pestanas"),
    ("Any slot on Tuesday afternoon for a manicure?", "manos_pies"),
    ("Quiero depilarme las piernas", "depilacion"),
    ("¿Cuánto cuesta?", None),
])
def test_category_in_text(text, expected):
    assert intents.category_in_text(text) == expected


@pytest.mark.parametrize("reply,claims", [
    ("We don't have any openings on Tuesday afternoon.", True),
    ("Our opening hours are 10:00 to 20:00.", False),
])
def test_claims_availability_catches_openings(reply, claims):
    assert intents.claims_availability(reply) is claims
