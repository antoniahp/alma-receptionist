from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from domain.exceptions import LanguageModelUnavailable
from infrastructure import dependencies


class Command(BaseCommand):
    help = "Comprueba que la IA (Ollama local o Ollama Cloud) responde con el modelo configurado."

    def handle(self, *args, **options):
        self.stdout.write(
            f"OLLAMA_URL={settings.OLLAMA_URL}  OLLAMA_MODEL={settings.OLLAMA_MODEL}  clave={'sí' if settings.OLLAMA_API_KEY else 'no'}"
        )
        service = dependencies.get_language_model_service()
        if not service.is_available():
            raise CommandError("La IA no está disponible. Mira el aviso de arriba (clave, modelo o URL).")
        try:
            answer = service.write_text("Saluda en una frase corta, en español, como recepcionista de un centro de estética.")
        except LanguageModelUnavailable as error:
            raise CommandError(f"La IA no responde: {error}") from error
        self.stdout.write(self.style.SUCCESS(f"Responde: {answer}"))
