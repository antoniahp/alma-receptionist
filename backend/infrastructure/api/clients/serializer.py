from rest_framework import serializers


class CreateClientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")
    email = serializers.CharField(max_length=254, required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateClientSerializer(CreateClientSerializer):
    accepts_reminders = serializers.BooleanField(required=False, default=True)
