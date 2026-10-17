from django.apps import AppConfig


class InfrastructureConfig(AppConfig):
    """Capa de infraestructura: API, admin, adaptadores (Telegram, IA, email) y comandos de consola."""

    name = "infrastructure"
    verbose_name = "Infraestructura"

    def ready(self):
        # Avisos emergentes a la dueña cuando pasa algo (ver owner_push_alerts.py)
        from infrastructure import owner_push_alerts

        owner_push_alerts.connect()
