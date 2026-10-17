from rest_framework import serializers


class UpdateSupplierEmailSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=254)
