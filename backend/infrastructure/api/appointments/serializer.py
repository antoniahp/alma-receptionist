from rest_framework import serializers


class CreateAppointmentSerializer(serializers.Serializer):
    client = serializers.UUIDField()
    service = serializers.UUIDField()
    start = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class AppointmentFiltersSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    status = serializers.CharField(required=False)
