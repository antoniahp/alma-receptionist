from rest_framework import serializers

from domain.entities import Service


class ServiceFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    category = serializers.ChoiceField(choices=Service.CATEGORIES)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    name_en = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    description_en = serializers.CharField(required=False, allow_blank=True, default="")
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = serializers.IntegerField()
    repeat_every_days = serializers.IntegerField(required=False, allow_null=True, default=None)
    active = serializers.BooleanField(required=False, default=True)
