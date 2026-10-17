from datetime import time, timedelta
from types import SimpleNamespace

import pytest
from django.core.cache import cache
from django.utils import timezone
from model_bakery import baker

from infrastructure.repositories.django_repositories import build_django_repositories
from tests.fakes import FakeEmailService, FakeLanguageModelService, FakeMessageService


@pytest.fixture(autouse=True)
def empty_cache():
    """Cada test empieza sin nada guardado en memoria (enlaces de tiendas, etc.)."""
    cache.clear()


@pytest.fixture(autouse=True)
def test_settings(settings):
    settings.LLM_ENABLED = False
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.TELEGRAM_BOT_USERNAME = "alma_bot"
    settings.TELEGRAM_OWNER_CHAT_ID = "999"
    settings.BUSINESS = {
        "name": "Centro de prueba",
        "owner": "Cris",
        "address": "Calle Falsa 1",
        "phone": "600 000 000",
        "assistant_name": "Aura",
        "legal_name": "Cris Prueba",
        "nif": "00000000T",
        "email": "hola@centro.example",
    }
    settings.PUBLIC_SITE_URL = "https://centro.example"
    settings.GOOGLE_REVIEW_URL = ""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    return settings


@pytest.fixture
def repositories(db):
    return build_django_repositories()


@pytest.fixture
def message_service():
    return FakeMessageService()


@pytest.fixture
def language_model_service():
    return FakeLanguageModelService()


@pytest.fixture
def email_service():
    return FakeEmailService()


@pytest.fixture
def next_monday():
    today = timezone.localdate()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


@pytest.fixture
def salon(db):
    """Centro abierto de lunes a sábado (10-14 y 16-20) con un masaje que gasta aceite."""
    for weekday in range(6):
        baker.make("domain.OpeningHours", weekday=weekday, opens=time(10), closes=time(14))
        baker.make("domain.OpeningHours", weekday=weekday, opens=time(16), closes=time(20))
    supplier = baker.make("domain.Supplier", name="Aromas del Sur", contact_name="Pilar", email="pedidos@aromas.example")
    oil = baker.make(
        "domain.Product",
        name="Aceite de almendras",
        reference="AC-500",
        supplier=supplier,
        unit_price=15,
        uses_per_unit=5,
        stock_uses=4,
        min_uses=3,
    )
    massage = baker.make(
        "domain.Service",
        name="Masaje relajante",
        duration_minutes=60,
        price=45,
        repeat_every_days=30,
        keywords="masaje,espalda",
        active=True,
        description="",
    )
    baker.make("domain.ServiceProduct", service=massage, product=oil, uses=1)
    laura = baker.make("domain.Client", name="Laura Gómez", phone="611111111", telegram_chat_id=None)
    return SimpleNamespace(supplier=supplier, oil=oil, massage=massage, laura=laura)
