import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea el usuario de la dueña a partir de OWNER_USERNAME y OWNER_PASSWORD si todavía no existe (útil en Render)."

    def handle(self, *args, **options):
        username = os.getenv("OWNER_USERNAME", "").strip()
        password = os.getenv("OWNER_PASSWORD", "")
        if not username or not password:
            self.stdout.write("OWNER_USERNAME u OWNER_PASSWORD no están definidos: no se crea ningún usuario.")
            return
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"El usuario {username} ya existe.")
            return
        user_model.objects.create_superuser(username=username, password=password, first_name=username.title())
        self.stdout.write(self.style.SUCCESS(f"Usuario {username} creado."))
