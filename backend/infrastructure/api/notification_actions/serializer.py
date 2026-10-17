from rest_framework import serializers


class SendReactivationSerializer(serializers.Serializer):
    client = serializers.UUIDField()
    service = serializers.UUIDField()


class SentCountSerializer(serializers.Serializer):
    reminders = serializers.IntegerField()
    reactivations = serializers.IntegerField()
    reviews = serializers.IntegerField(default=0)
