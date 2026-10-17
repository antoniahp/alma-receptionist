"""Ficha de la clienta y datos que se pueden cambiar (los mismos que al darla de alta)."""

from rest_framework import serializers

from infrastructure.api.clients.serializer import UpdateClientSerializer
from infrastructure.api.shared.serializers import AppointmentSerializer, ClientSerializer, PackSerializer

__all__ = ["ClientFileSerializer", "UpdateClientSerializer"]


class ClientFileSerializer(serializers.Serializer):
    client = ClientSerializer()
    privacy_accepted_at = serializers.DateTimeField(source="client.privacy_accepted_at", allow_null=True)
    appointments = AppointmentSerializer(many=True)
    packs = PackSerializer(many=True)
    visits = serializers.IntegerField()
    spent = serializers.DecimalField(max_digits=10, decimal_places=2)
