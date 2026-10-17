from rest_framework import serializers


class AddToShoppingListSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    store = serializers.CharField(max_length=120)
    title = serializers.CharField(max_length=300, allow_blank=True, required=False, default="")
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    # Los enlaces de las tiendas y de Google Shopping son largos y llevan parámetros raros: no los validamos como URL estricta
    link = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="")
    units = serializers.IntegerField(min_value=1, max_value=99, required=False, default=1)
    page_token = serializers.CharField(max_length=4000, allow_blank=True, required=False, default="")
