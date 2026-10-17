from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from domain.exceptions import MessageNotSent
from infrastructure import dependencies


class Command(BaseCommand):
    help = "Envía un correo de prueba para comprobar la configuración de correo. Uso: python manage.py send_test_email tu@correo.com"

    def add_arguments(self, parser):
        parser.add_argument("to", help="Dirección a la que enviar el correo de prueba")

    def handle(self, *args, **options):
        if settings.EMAIL_BACKEND.endswith("console.EmailBackend"):
            self.stdout.write(self.style.WARNING("EMAIL_BACKEND es el de consola: el correo solo se mostrará aquí, no se enviará."))
        try:
            dependencies.get_email_service().send(
                options["to"],
                f"Prueba de correo de {settings.BUSINESS['name']}",
                "Si lees esto, el correo de Alma funciona. Los pedidos a proveedores saldrán desde esta misma cuenta.",
            )
        except MessageNotSent as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS(f"Correo enviado a {options['to']}"))
