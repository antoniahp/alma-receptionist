from django.core.management.base import BaseCommand

from application.commands.send_due_notifications.command import SendDueNotificationsCommand
from application.commands.send_due_notifications.command_dto import SendDueNotificationsCommandDTO
from infrastructure import dependencies


class Command(BaseCommand):
    help = "Envía los recordatorios y mensajes para repetir pendientes (para usar con cron si el bot no está encendido)."

    def handle(self, *args, **options):
        command = SendDueNotificationsCommand(
            dependencies.get_repositories(), dependencies.get_message_service(), dependencies.get_language_model_service()
        )
        sent = command.execute(SendDueNotificationsCommandDTO())
        self.stdout.write(f"Recordatorios: {sent['reminders']} · Para repetir: {sent['reactivations']}")
