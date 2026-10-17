from abc import ABC, abstractmethod


class LanguageModelService(ABC):
    """Modelo de lenguaje open-weight (Gemma en local con Ollama)."""

    @abstractmethod
    def is_available(self):
        """True si el modelo está instalado y responde."""

    @abstractmethod
    def write_text(self, prompt, temperature=0.6):
        """Devuelve texto. Lanza LanguageModelUnavailable si no responde."""

    @abstractmethod
    def write_json(self, messages, schema, temperature=0.6):
        """Devuelve un dict que cumple el JSON schema. Lanza LanguageModelUnavailable si no responde."""
