from rest_framework import serializers

from infrastructure.api.shared.serializers import AppointmentSerializer, ClientSerializer


class PendingReminderSerializer(serializers.Serializer):
    appointment = AppointmentSerializer()
    text = serializers.CharField()


class ServiceNameSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class PendingReactivationSerializer(serializers.Serializer):
    client = ClientSerializer()
    service = ServiceNameSerializer()
    days_since = serializers.IntegerField()
    days_until_due = serializers.IntegerField()
    preview = serializers.CharField()
    slots = serializers.ListField(child=serializers.CharField())


class PendingNotificationsSerializer(serializers.Serializer):
    reminders = PendingReminderSerializer(many=True)
    reactivations = PendingReactivationSerializer(many=True)
