"""Adaptador del modelo open-weight servido en local con Ollama (por defecto Gemma)."""

import json
import logging
import time

import requests
from django.conf import settings

from domain.exceptions import LanguageModelUnavailable
from domain.services.language_model_service import LanguageModelService

logger = logging.getLogger(__name__)
STATUS_CACHE_SECONDS = 30


class OllamaLanguageModelService(LanguageModelService):
    """Sirve para Ollama en local (sin clave) y para Ollama Cloud (OLLAMA_URL=https://ollama.com y OLLAMA_API_KEY)."""

    # Se comparte entre instancias para no preguntar a Ollama en cada mensaje
    last_check = {"available": None, "checked_at": 0.0}

    def headers(self):
        if settings.OLLAMA_API_KEY:
            return {"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}
        return {}

    def is_available(self):
        if not settings.LLM_ENABLED:
            return False
        cache = OllamaLanguageModelService.last_check
        if cache["available"] is not None and time.time() - cache["checked_at"] < STATUS_CACHE_SECONDS:
            return cache["available"]
        available = self.check_model_is_installed()
        OllamaLanguageModelService.last_check = {"available": available, "checked_at": time.time()}
        return available

    def check_model_is_installed(self):
        try:
            response = requests.get(f"{settings.OLLAMA_URL}/api/tags", headers=self.headers(), timeout=5)
            if response.status_code == 401:
                logger.warning("Ollama rechaza la clave: revisa OLLAMA_API_KEY")
                return False
            names = [model.get("name", "") for model in response.json().get("models", [])]
        except (requests.RequestException, ValueError):
            return False
        model = settings.OLLAMA_MODEL
        installed = any(name == model or name.startswith(model + ":") for name in names)
        if not installed:
            logger.warning("Ollama no tiene el modelo %s. Modelos disponibles: %s", model, ", ".join(names[:15]))
        return installed

    def chat(self, messages, schema=None, temperature=0.6):
        if not self.is_available():
            raise LanguageModelUnavailable("El modelo local no está disponible")
        payload = {"model": settings.OLLAMA_MODEL, "messages": messages, "stream": False, "options": {"temperature": temperature}}
        if schema:
            payload["format"] = schema
        try:
            response = requests.post(f"{settings.OLLAMA_URL}/api/chat", json=payload, headers=self.headers(), timeout=settings.LLM_TIMEOUT)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except (requests.RequestException, KeyError, ValueError) as error:
            OllamaLanguageModelService.last_check = {"available": False, "checked_at": time.time()}
            raise LanguageModelUnavailable(str(error)) from error

    def write_text(self, prompt, temperature=0.6):
        return self.chat([{"role": "user", "content": prompt}], temperature=temperature).strip()

    def write_json(self, messages, schema, temperature=0.6):
        content = self.chat(messages, schema=schema, temperature=temperature)
        try:
            data = json.loads(content)
        except ValueError as error:
            raise LanguageModelUnavailable("Respuesta no válida del modelo") from error
        if not isinstance(data, dict):
            raise LanguageModelUnavailable("Respuesta no válida del modelo")
        return data
