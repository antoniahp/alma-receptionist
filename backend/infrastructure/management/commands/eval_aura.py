"""Mide a Aura con mensajes típicos de clientas: Gemma (con sus salvaguardas) frente a las respuestas fijas.

    python manage.py eval_aura            # las dos y la comparación
    python manage.py eval_aura --mode ai  # solo Gemma

Cada mensaje va en una conversación nueva dentro de una transacción que se deshace al terminar:
no se guarda nada, no se crean citas ni preguntas de verdad y a la dueña no le llega ningún aviso
(ni Telegram ni notificaciones: los avisos solo salen cuando se confirma la transacción, y aquí nunca se confirma).
"""

import csv
import logging
import re
import statistics
import time
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from application.commands.handle_chat_message.command import HandleChatMessageCommand
from application.commands.handle_chat_message.command_dto import HandleChatMessageCommandDTO
from application.shared.ai_receptionist import outcome_of
from domain.entities import Conversation, HelpRequest
from domain.exceptions import LanguageModelUnavailable
from domain.rules import language
from domain.services.language_model_service import LanguageModelService
from domain.services.message_service import MessageService
from infrastructure import dependencies
from infrastructure.management.commands.aura_eval_cases import CASES

SPANISH_WORDS = re.compile(r"[¿¡ñ]|\b(el|la|los|las|que|para|tu|tus|cita|precio|hola|gracias|te|con|por)\b", re.I)
ENGLISH_WORDS = re.compile(r"\b(the|you|your|for|is|are|we|our|appointment|price|hi|thanks|with|can|would)\b", re.I)


class Recorder(LanguageModelService):
    """Envuelve el modelo para apuntar tiempo y tokens de cada llamada."""

    def __init__(self, service):
        self.service = service
        self.calls = []
        self.errors = []

    def is_available(self):
        return self.service.is_available()

    def write_text(self, prompt, temperature=0.6):
        return self.service.write_text(prompt, temperature)

    def write_json(self, messages, schema, temperature=0.6):
        started = time.monotonic()
        try:
            return self.service.write_json(messages, schema, temperature)
        except LanguageModelUnavailable as error:
            self.errors.append(str(error))
            raise
        finally:
            usage = dict(getattr(self.service, "last_usage", None) or {})
            usage["wall_ms"] = round((time.monotonic() - started) * 1000)
            self.calls.append(usage)


class Off(LanguageModelService):
    """Modelo apagado: contestan las reglas."""

    def is_available(self):
        return False

    def write_text(self, prompt, temperature=0.6):
        raise LanguageModelUnavailable("apagado")

    def write_json(self, messages, schema, temperature=0.6):
        raise LanguageModelUnavailable("apagado")


class Silent(MessageService):
    """Nada sale de verdad: ni Telegram a la dueña ni mensajes a clientas."""

    def is_enabled(self):
        return False

    def send(self, chat_id, text, buttons=None):
        return None


def looks_english(text):
    return len(ENGLISH_WORDS.findall(text)) >= len(SPANISH_WORDS.findall(text))


def judge(expected, outcome, handed_off, text, pattern):
    if expected == "handoff":
        return handed_off
    if handed_off:
        return False
    if expected == "book":
        return outcome in ("slots", "booked", "choose_service")
    if expected == "stay":
        return outcome not in ("slots", "booked")
    if expected == "info":
        return pattern is None or re.search(pattern, text) is not None
    return False


class Command(BaseCommand):
    help = "Mide a Aura (Gemma frente a respuestas fijas) con mensajes típicos de clientas."

    def add_arguments(self, parser):
        parser.add_argument("--mode", choices=["ai", "rules", "both"], default="both")
        parser.add_argument("--limit", type=int, default=0, help="Solo los N primeros mensajes (para probar)")
        parser.add_argument("--out", default="eval_results")
        parser.add_argument("--chats-per-month", type=int, default=300)
        parser.add_argument("--messages-per-chat", type=int, default=4)

    def handle(self, *args, **options):
        cases = CASES[: options["limit"]] if options["limit"] else CASES
        modes = ["rules", "ai"] if options["mode"] == "both" else [options["mode"]]
        if "ai" in modes and not dependencies.get_language_model_service().is_available():
            raise CommandError("La IA no está disponible: ejecuta antes python manage.py check_ai")

        # Sin las trazas de cada llamada en pantalla: el resultado sale al final
        for name in ("application", "infrastructure"):
            logging.getLogger(name).setLevel(logging.ERROR)

        rows = []
        for mode in modes:
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n== {mode.upper()} ({len(cases)} mensajes) =="))
            for number, case in enumerate(cases, 1):
                row = self.run_case(mode, *case)
                rows.append(row)
                mark = self.style.SUCCESS("✓") if row["ok"] else self.style.ERROR("✗")
                self.stdout.write(f"{mark} {number:>2} [{row['lang']}] {row['expected']:<7} → {row['outcome']:<14} {row['message'][:55]}")

        out = Path(options["out"])
        out.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        csv_path = out / f"aura-eval-{stamp}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        summary = self.summary(rows, modes, options)
        (out / f"aura-eval-{stamp}.md").write_text(summary, encoding="utf-8")
        self.stdout.write("\n" + summary)
        self.stdout.write(self.style.SUCCESS(f"\nGuardado en {csv_path} y {csv_path.with_suffix('.md')}"))

    def run_case(self, mode, lang, message, expected, pattern):
        model = Recorder(dependencies.get_language_model_service()) if mode == "ai" else Off()
        key = f"{Conversation.WEB_PREFIX}eval-{uuid.uuid4()}"
        started = time.monotonic()
        with transaction.atomic(), language.use(lang):
            before = HelpRequest.objects.count()
            command = HandleChatMessageCommand(dependencies.get_repositories(), Silent(), model)
            reply = command.execute(HandleChatMessageCommandDTO(conversation_key=key, text=message))
            handed_off = HelpRequest.objects.count() > before
            transaction.set_rollback(True)
        elapsed = round((time.monotonic() - started) * 1000)

        calls = getattr(model, "calls", [])
        errors = getattr(model, "errors", [])
        if mode == "rules":
            answered_by = "rules"
        elif not calls:
            answered_by = "guard"  # lo resolvió el código antes de llegar al modelo (fuera de tema, salud)
        elif errors:
            answered_by = "fallback"
        else:
            answered_by = "gemma"
        outcome = "handoff" if handed_off else outcome_of(reply)
        return {
            "mode": mode,
            "lang": lang,
            "expected": expected,
            "message": message,
            "outcome": outcome,
            "ok": judge(expected, outcome, handed_off, reply.text, pattern),
            "right_language": looks_english(reply.text) == (lang == "en"),
            "answered_by": answered_by,
            "ms": elapsed,
            "prompt_tokens": sum(call.get("prompt_tokens", 0) for call in calls),
            "output_tokens": sum(call.get("output_tokens", 0) for call in calls),
            "reply": reply.text.replace("\n", " "),
        }

    def summary(self, rows, modes, options):
        groups = [("book", "Pide cita → ofrece huecos"), ("info", "Pregunta → contesta ella"),
                  ("handoff", "Salud o duda → pasa a Cris"), ("stay", "Fuera de tema → no se sale")]
        names = {"rules": "Respuestas fijas", "ai": f"Gemma ({settings.OLLAMA_MODEL}) + salvaguardas"}

        def pct(selected):
            return f"{sum(r['ok'] for r in selected) / len(selected) * 100:.0f}% ({sum(r['ok'] for r in selected)}/{len(selected)})" if selected else "—"

        lines = [f"# Evaluación de Aura · {datetime.now():%Y-%m-%d %H:%M}", "", "| | " + " | ".join(names[m] for m in modes) + " |",
                 "|---|" + "---|" * len(modes)]
        for key, label in groups:
            lines.append(f"| {label} | " + " | ".join(pct([r for r in rows if r["mode"] == m and r["expected"] == key]) for m in modes) + " |")
        lines.append("| **Total** | " + " | ".join(f"**{pct([r for r in rows if r['mode'] == m])}**" for m in modes) + " |")
        lines.append("| Contesta en el idioma de la clienta | " + " | ".join(
            pct([dict(r, ok=r["right_language"]) for r in rows if r["mode"] == m]) for m in modes) + " |")

        ai = [r for r in rows if r["mode"] == "ai"]
        if ai:
            gemma = [r for r in ai if r["answered_by"] == "gemma"]
            times = sorted(r["ms"] for r in gemma) or [0]
            prompt = [r["prompt_tokens"] for r in gemma] or [0]
            output = [r["output_tokens"] for r in gemma] or [0]
            per_month = options["chats_per_month"] * options["messages_per_chat"]
            lines += [
                "",
                "## Gemma",
                f"- Contestó Gemma: {len(gemma)} · lo resolvió el código antes (fuera de tema / salud): "
                f"{sum(r['answered_by'] == 'guard' for r in ai)} · fallo del modelo y contestaron las reglas: {sum(r['answered_by'] == 'fallback' for r in ai)}",
                f"- Tiempo de respuesta: mediana {statistics.median(times) / 1000:.1f} s · p90 {times[int(len(times) * 0.9) - 1 if len(times) > 1 else 0] / 1000:.1f} s",
                f"- Tokens por mensaje: {statistics.mean(prompt):.0f} de entrada + {statistics.mean(output):.0f} de salida",
                f"- Al mes ({options['chats_per_month']} conversaciones × {options['messages_per_chat']} mensajes = {per_month} mensajes): "
                f"~{per_month * statistics.mean(prompt) / 1e6:.2f} M tokens de entrada + {per_month * statistics.mean(output) / 1e6:.2f} M de salida",
            ]
        failed = [r for r in rows if not r["ok"]]
        if failed:
            lines += ["", "## Fallos (para revisar a mano)", "", "| Modo | Mensaje | Esperado | Pasó | Respuesta |", "|---|---|---|---|---|"]
            lines += [f"| {r['mode']} | {r['message']} | {r['expected']} | {r['outcome']} | {r['reply'][:120]} |" for r in failed]
        return "\n".join(lines) + "\n"
