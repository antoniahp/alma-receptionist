from decimal import Decimal

from rest_framework import serializers


class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=160)
    unit_price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0"))
    uses_per_unit = serializers.IntegerField(min_value=1, max_value=10000)
    units_in_stock = serializers.IntegerField(min_value=0, max_value=10000)
    min_units = serializers.IntegerField(min_value=0, max_value=10000)
    supplier_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    new_supplier_name = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    service_ids = serializers.ListField(child=serializers.UUIDField(), required=False, default=list)


class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    supplier = serializers.CharField(source="supplier.name")
    unit_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    uses_per_unit = serializers.IntegerField()
    stock_uses = serializers.IntegerField()
    min_uses = serializers.IntegerField()
