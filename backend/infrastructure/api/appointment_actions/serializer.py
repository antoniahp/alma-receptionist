from rest_framework import serializers

from domain.entities import payment
from infrastructure.api.shared.serializers import AppointmentSerializer


class CompleteAppointmentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=payment.METHODS, required=False, default=payment.CASH)


class UsedProductSerializer(serializers.Serializer):
    product = serializers.CharField()
    uses = serializers.IntegerField()


class CompletedAppointmentSerializer(serializers.Serializer):
    appointment = AppointmentSerializer()
    used = UsedProductSerializer(many=True)
