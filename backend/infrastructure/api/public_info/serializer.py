from rest_framework import serializers

from infrastructure.api.shared.localized import localized


class PublicCategorySerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()


class PublicServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    category = serializers.CharField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    duration_minutes = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)

    def get_name(self, service):
        return localized(service, "name")

    def get_description(self, service):
        return localized(service, "description")


class PublicInfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()
    owner = serializers.CharField()
    assistant_name = serializers.CharField()
    legal_name = serializers.CharField(allow_blank=True)
    nif = serializers.CharField(allow_blank=True)
    email = serializers.CharField(allow_blank=True)
    hours = serializers.CharField()
    telegram_bot = serializers.CharField(allow_blank=True)
    demo_login = serializers.DictField(allow_null=True)
    categories = PublicCategorySerializer(many=True)
    services = PublicServiceSerializer(many=True)
