from decimal import Decimal

from rest_framework import serializers

MONEY = {"max_digits": 10, "decimal_places": 2}


class CashDayParamsSerializer(serializers.Serializer):
    day = serializers.DateField(required=False)


class CloseCashSerializer(serializers.Serializer):
    day = serializers.DateField()
    counted_cash = serializers.DecimalField(**MONEY, min_value=Decimal("0"))
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class CashClosingSerializer(serializers.Serializer):
    expected_cash = serializers.DecimalField(**MONEY)
    counted_cash = serializers.DecimalField(**MONEY)
    difference = serializers.DecimalField(**MONEY)
    notes = serializers.CharField()
    closed_at = serializers.DateTimeField()


class ChargeSerializer(serializers.Serializer):
    time = serializers.DateTimeField()
    client_name = serializers.CharField()
    concept = serializers.CharField()
    payment_method = serializers.CharField()
    amount = serializers.DecimalField(**MONEY)


class CashDaySerializer(serializers.Serializer):
    day = serializers.DateField()
    cash = serializers.DecimalField(**MONEY)
    card = serializers.DecimalField(**MONEY)
    bizum = serializers.DecimalField(**MONEY)
    total = serializers.DecimalField(**MONEY)
    appointments = serializers.IntegerField()
    sessions_with_pack = serializers.IntegerField()
    packs_sold = serializers.IntegerField()
    charges = ChargeSerializer(many=True)
    closing = CashClosingSerializer(allow_null=True)
