from rest_framework import serializers


class PriceOfferSerializer(serializers.Serializer):
    store = serializers.CharField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    link = serializers.CharField()
    page_token = serializers.CharField(allow_blank=True)
    trusted = serializers.BooleanField()


class PriceComparisonSerializer(serializers.Serializer):
    product = serializers.CharField(source="product.name")
    supplier = serializers.CharField(source="product.supplier.name")
    our_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    offers = PriceOfferSerializer(many=True)
    cheapest = PriceOfferSerializer(allow_null=True)
    saving = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    discarded = serializers.IntegerField()
    unverified = serializers.IntegerField()
