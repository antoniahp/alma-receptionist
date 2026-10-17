from rest_framework import serializers


class TimeBlockSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    reason = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")


class DaysRangeSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
