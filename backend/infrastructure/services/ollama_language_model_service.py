"""Adaptador del modelo open-weight servido en local con Ollama (por defecto Gemma)."""

import json
import logging
import re
import time

import requests
from django.conf import settings

from domain.exceptions import LanguageModelUnavailable
from domain.services.language_model_service import LanguageModelService

logger = logging.getLogger(__name__)
STATUS_CACHE_SECONDS = 30
FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def extract_json_object(text):
    """El JSON de la respuesta, aunque el modelo lo envuelva en ```json ... ``` o le ponga texto alrededor."""
    text = FENCE.sub("", (text or "").strip())
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


class OllamaLanguageModelService(LanguageModelService):
    """Sirve para Ollama en local (sin clave) y para Ollama Cloud (OLLAMA_URL=https://ollama.com y OLLAMA_API_KEY)."""

    # Se comparte entre instancias para no preguntar a Ollama en cada mensaje
    last_check = {"available": None, "checked_at": 0.0}
    last_usage = None

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
        # think=False: los modelos que "razonan" antes de responder (como Gemma 4) contestan directamente,
        # más rápido y más barato, y el JSON llega en la respuesta y no mezclado con el razonamiento.
        payload = {"model": settings.OLLAMA_MODEL, "messages": messages, "stream": False, "think": False, "options": {"temperature": temperature}}
        if schema:
            payload["format"] = schema
        started = time.monotonic()
        try:
            response = self.post(payload)
            if response.status_code == 400 and "think" in response.text.lower():
                # Modelo que no admite la opción "think": se repite sin ella
                payload.pop("think")
                response = self.post(payload)
            response.raise_for_status()
            body = response.json()
            content = body["message"]["content"]
        except (requests.RequestException, KeyError, ValueError) as error:
            OllamaLanguageModelService.last_check = {"available": False, "checked_at": time.time()}
            logger.warning("gemma_error model=%s ms=%d error=%s", settings.OLLAMA_MODEL, (time.monotonic() - started) * 1000, type(error).__name__)
            raise LanguageModelUnavailable(str(error)) from error
        # Traza de cada llamada (se ve en los logs de Render): modelo, tiempo y tokens que cobra el proveedor
        self.last_usage = {
            "model": settings.OLLAMA_MODEL,
            "ms": round((time.monotonic() - started) * 1000),
            "prompt_tokens": body.get("prompt_eval_count") or 0,
            "output_tokens": body.get("eval_count") or 0,
        }
        logger.info(
            "gemma_call model=%s ms=%d prompt_tokens=%d output_tokens=%d json=%s",
            self.last_usage["model"], self.last_usage["ms"], self.last_usage["prompt_tokens"], self.last_usage["output_tokens"], bool(schema),
        )
        return content

    def post(self, payload):
        return requests.post(f"{settings.OLLAMA_URL}/api/chat", json=payload, headers=self.headers(), timeout=settings.LLM_TIMEOUT)

    def write_text(self, prompt, temperature=0.6):
        return self.chat([{"role": "user", "content": prompt}], temperature=temperature).strip()

    def write_json(self, messages, schema, temperature=0.6):
        content = self.chat(messages, schema=schema, temperature=temperature)
        try:
            data = extract_json_object(content)
        except ValueError as error:
            snippet = (content or "").strip().replace("\n", " ")[:120] or "(vacía)"
            logger.warning("gemma_bad_json model=%s content=%s", settings.OLLAMA_MODEL, snippet)
            raise LanguageModelUnavailable(f"Respuesta no válida del modelo: {snippet}") from error
        if not isinstance(data, dict):
            raise LanguageModelUnavailable("Respuesta no válida del modelo")
        return data
