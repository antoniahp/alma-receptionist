from django.conf import settings


class GetSystemStatusQuery:
    """Si la IA local y Telegram están funcionando (se muestra en el panel)."""

    def __init__(self, language_model_service, message_service):
        self.language_model_service = language_model_service
        self.message_service = message_service

    def execute(self, dto):
        return {
            "business": settings.BUSINESS,
            "demo": settings.DEMO_MODE,
            "llm": {
                "available": self.language_model_service.is_available(),
                "model": settings.OLLAMA_MODEL,
                "enabled": settings.LLM_ENABLED,
            },
            "telegram": {
                "enabled": self.message_service.is_enabled(),
                "bot_username": settings.TELEGRAM_BOT_USERNAME,
                "owner_alerts": bool(settings.TELEGRAM_OWNER_CHAT_ID),
            },
        }
