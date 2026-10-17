from rest_framework import serializers


class ChangeUnitsSerializer(serializers.Serializer):
    units = serializers.IntegerField(min_value=1, max_value=99)
