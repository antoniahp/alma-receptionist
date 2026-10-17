from rest_framework import serializers


class CountStockSerializer(serializers.Serializer):
    uses_in_stock = serializers.IntegerField(min_value=0, max_value=1000000)
