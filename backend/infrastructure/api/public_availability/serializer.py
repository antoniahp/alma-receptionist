from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers


class AvailabilityFiltersSerializer(serializers.Serializer):
    service = serializers.UUIDField()
    date = serializers.DateField()

    def validate_date(self, value):
        today = timezone.localdate()
        if value < today or value > today + timedelta(days=settings.BOOKING_DAYS_AHEAD):
            raise serializers.ValidationError("Solo se puede reservar desde hoy y hasta tres semanas vista.")
        return value


class AvailabilitySerializer(serializers.Serializer):
    slots = serializers.SerializerMethodField()

    def get_slots(self, slots):
        return [timezone.localtime(slot).isoformat() for slot in slots]
