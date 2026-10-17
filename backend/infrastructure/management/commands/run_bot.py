"""Bot de Telegram (long polling) y envío automático de avisos cada minuto.

python manage.py run_bot
"""

import logging
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections

from application.commands.send_due_notifications.command import SendDueNotificationsCommand
from application.commands.send_due_notifications.command_dto import SendDueNotificationsCommandDTO
from domain.exceptions import MessageNotSent
from infrastructure import dependencies
from infrastructure.telegram_bot.update_handler import TelegramUpdateHandler

logger = logging.getLogger(__name__)
SECONDS_BETWEEN_NOTIFICATIONS = 60
SECONDS_TO_WAIT_AFTER_ERROR = 5


class Command(BaseCommand):
    help = "Arranca el bot de Telegram y el envío automático de recordatorios."

    def add_arguments(self, parser):
        parser.add_argument("--no-scheduler", action="store_true", help="No enviar recordatorios automáticamente")

    def handle(self, *args, **options):
        repositories = dependencies.get_repositories()
        telegram = dependencies.get_message_service()
        language_model = dependencies.get_language_model_service()
        if not telegram.is_enabled():
            raise CommandError("Falta TELEGRAM_BOT_TOKEN en backend/.env (créalo hablando con @BotFather).")

        handler = TelegramUpdateHandler(repositories, telegram, language_model)
        self.stdout.write(self.style.SUCCESS("Bot en marcha. Ctrl+C para parar."))
        offset = None
        last_notifications_run = 0.0
        while True:
            try:
                for update in telegram.get_updates(offset):
                    offset = update["update_id"] + 1
                    try:
                        handler.handle(update)
                    except Exception:  # un mensaje raro no debe parar el bot
                        logger.exception("Error procesando un mensaje de Telegram")
            except MessageNotSent as error:
                logger.warning("Telegram: %s. Reintento en %s s", error, SECONDS_TO_WAIT_AFTER_ERROR)
                time.sleep(SECONDS_TO_WAIT_AFTER_ERROR)

            if not options["no_scheduler"] and time.time() - last_notifications_run > SECONDS_BETWEEN_NOTIFICATIONS:
                last_notifications_run = time.time()
                try:
                    sent = SendDueNotificationsCommand(repositories, telegram, language_model).execute(SendDueNotificationsCommandDTO())
                    if any(sent.values()):
                        logger.info("Avisos enviados: %s", sent)
                except Exception:
                    logger.exception("Error enviando avisos")
            close_old_connections()
