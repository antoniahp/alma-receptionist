from decimal import Decimal

from rest_framework import serializers

from domain.entities import payment


class SellPackSerializer(serializers.Serializer):
    client = serializers.UUIDField()
    service = serializers.UUIDField()
    sessions = serializers.IntegerField(min_value=2, max_value=50)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0"))
    payment_method = serializers.ChoiceField(choices=payment.PACK_SALE_METHODS)
