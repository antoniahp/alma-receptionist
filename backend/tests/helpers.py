from datetime import datetime, time

from django.utils import timezone


def local_datetime(day, hour, minute=0):
    """Fecha y hora en la zona horaria del centro."""
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


def button_data(reply):
    """Todos los datos de los botones de una respuesta, en una lista plana."""
    return [button.data for row in reply.buttons for button in row]
