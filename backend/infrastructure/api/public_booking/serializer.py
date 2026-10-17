from rest_framework import serializers

from domain.rules import spanish_format as fmt
from infrastructure.api.shared.localized import localized
from infrastructure.services.telegram_message_service import telegram_deep_link


class PublicBookingSerializer(serializers.Serializer):
    service = serializers.UUIDField()
    start = serializers.DateTimeField()
    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")
    privacy_accepted = serializers.BooleanField(default=False)


class BookedAppointmentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    service = serializers.SerializerMethodField()
    start = serializers.DateTimeField()
    when = serializers.SerializerMethodField()
    client_name = serializers.CharField(source="client.first_name")
    telegram_link = serializers.SerializerMethodField()

    def get_service(self, appointment):
        return localized(appointment.service, "name")

    def get_when(self, appointment):
        return f"{fmt.day_long(appointment.start)} a las {fmt.hour(appointment.start)}"

    def get_telegram_link(self, appointment):
        return telegram_deep_link(appointment.client)
