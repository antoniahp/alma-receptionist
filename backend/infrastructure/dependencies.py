"""Aquí se decide qué implementación real usa cada repositorio y cada servicio. Los tests usan versiones falsas."""

from django.conf import settings

from infrastructure.repositories.django_repositories import build_django_repositories
from infrastructure.services.demo_email_service import DemoEmailService
from infrastructure.services.django_email_service import DjangoEmailService
from infrastructure.services.ollama_language_model_service import OllamaLanguageModelService
from infrastructure.services.serpapi_price_search_service import SerpApiPriceSearchService
from infrastructure.services.telegram_message_service import TelegramMessageService
from infrastructure.services.web_push_service import WebPushService


def get_repositories():
    return build_django_repositories()


def get_message_service():
    return TelegramMessageService()


def get_language_model_service():
    return OllamaLanguageModelService()


def get_email_service():
    if settings.DEMO_MODE:
        return DemoEmailService()
    return DjangoEmailService()


def get_price_search_service():
    return SerpApiPriceSearchService()


def get_push_service():
    return WebPushService()
