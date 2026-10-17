from rest_framework import serializers

from infrastructure.api.shared.localized import localized


class ConsumptionSerializer(serializers.Serializer):
    product = serializers.UUIDField(source="product_id")
    product_name = serializers.CharField(source="product.name")
    uses = serializers.IntegerField()


class ServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    category = serializers.CharField()
    category_label = serializers.CharField(source="get_category_display")
    name = serializers.CharField()
    # El nombre para enseñar, en el idioma del panel (name/name_en son los que se editan)
    display_name = serializers.SerializerMethodField()
    description = serializers.CharField()
    name_en = serializers.CharField()
    description_en = serializers.CharField()
    keywords = serializers.CharField()
    duration_minutes = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    repeat_every_days = serializers.IntegerField(allow_null=True)
    active = serializers.BooleanField()
    consumption = ConsumptionSerializer(many=True, source="consumption.all")

    def get_display_name(self, service):
        return localized(service, "name")
