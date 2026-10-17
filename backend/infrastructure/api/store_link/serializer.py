from rest_framework import serializers


class StoreLinkSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=4000)
    store = serializers.CharField(max_length=120)
