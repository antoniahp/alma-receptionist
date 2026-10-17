from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from domain.exceptions import DomainError


def custom_exception_handler(exc, context):
    """Convierte los errores de negocio y los 'no existe' en respuestas claras para el frontend."""
    if isinstance(exc, DomainError):
        return Response({"detail": str(exc)}, status=exc.status_code)
    if isinstance(exc, ObjectDoesNotExist):
        return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)
    return exception_handler(exc, context)
