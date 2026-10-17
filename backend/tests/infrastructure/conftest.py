import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from infrastructure import dependencies
from tests.fakes import FakeEmailService, FakeLanguageModelService, FakeMessageService, FakePriceSearchService, FakePushService


@pytest.fixture(autouse=True)
def fake_services(monkeypatch):
    """Las vistas usan versiones falsas de Telegram, la IA y el correo (los repositorios son los reales de Django)."""
    message_service = FakeMessageService(enabled=False)
    language_model_service = FakeLanguageModelService()
    email_service = FakeEmailService()
    price_search_service = FakePriceSearchService()
    push_service = FakePushService()
    monkeypatch.setattr(dependencies, "get_message_service", lambda: message_service)
    monkeypatch.setattr(dependencies, "get_language_model_service", lambda: language_model_service)
    monkeypatch.setattr(dependencies, "get_email_service", lambda: email_service)
    monkeypatch.setattr(dependencies, "get_price_search_service", lambda: price_search_service)
    monkeypatch.setattr(dependencies, "get_push_service", lambda: push_service)
    return {
        "message_service": message_service,
        "language_model_service": language_model_service,
        "email_service": email_service,
        "price_search_service": price_search_service,
        "push_service": push_service,
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner_client(db):
    user = get_user_model().objects.create_user("cris", password="secreta123")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=user).key}")
    return client
