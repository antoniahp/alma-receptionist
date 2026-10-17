"""El adaptador de Ollama: pide respuesta directa (sin "razonar") y acepta el JSON aunque venga envuelto."""

import pytest

from domain.exceptions import LanguageModelUnavailable
from infrastructure.services import ollama_language_model_service as module
from infrastructure.services.ollama_language_model_service import OllamaLanguageModelService, extract_json_object


class FakeResponse:
    def __init__(self, content="", status=200, text=""):
        self.status_code = status
        self.text = text
        self._content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise module.requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return {"message": {"content": self._content}, "prompt_eval_count": 120, "eval_count": 30}


@pytest.fixture
def service(monkeypatch, settings):
    settings.LLM_ENABLED = True
    monkeypatch.setattr(OllamaLanguageModelService, "is_available", lambda self: True)
    return OllamaLanguageModelService()


def answer_with(monkeypatch, *responses):
    sent = []

    def fake_post(url, json, headers, timeout):
        sent.append(json)
        return responses[min(len(sent), len(responses)) - 1]

    monkeypatch.setattr(module.requests, "post", fake_post)
    return sent


@pytest.mark.parametrize(
    "content",
    [
        '{"reply": "Hola", "action": {"type": "none"}}',
        '```json\n{"reply": "Hola", "action": {"type": "none"}}\n```',
        'Aquí tienes:\n{"reply": "Hola", "action": {"type": "none"}}',
    ],
)
def test_reads_the_json_even_if_the_model_wraps_it(content):
    assert extract_json_object(content)["reply"] == "Hola"


def test_asks_the_model_to_answer_directly_without_thinking(service, monkeypatch):
    sent = answer_with(monkeypatch, FakeResponse('{"reply": "Hola"}'))

    assert service.write_json([{"role": "user", "content": "Hola"}], {"type": "object"}) == {"reply": "Hola"}
    assert sent[0]["think"] is False
    assert service.last_usage["prompt_tokens"] == 120


def test_retries_without_think_if_the_model_does_not_support_it(service, monkeypatch):
    sent = answer_with(monkeypatch, FakeResponse(status=400, text='{"error":"model does not support thinking"}'), FakeResponse('{"reply": "Hola"}'))

    assert service.write_json([{"role": "user", "content": "Hola"}], {"type": "object"}) == {"reply": "Hola"}
    assert "think" not in sent[1]


def test_an_unreadable_answer_says_what_came_back(service, monkeypatch):
    answer_with(monkeypatch, FakeResponse(""))

    with pytest.raises(LanguageModelUnavailable, match="vacía"):
        service.write_json([{"role": "user", "content": "Hola"}], {"type": "object"})
