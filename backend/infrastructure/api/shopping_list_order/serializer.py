from rest_framework import serializers


class OrderFromStoreSerializer(serializers.Serializer):
    store = serializers.CharField(max_length=120)
    bought_online = serializers.BooleanField()
