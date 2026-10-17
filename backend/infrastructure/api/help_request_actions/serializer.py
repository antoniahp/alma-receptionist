from rest_framework import serializers


class AnswerHelpRequestSerializer(serializers.Serializer):
    text = serializers.CharField(allow_blank=True)
    sign = serializers.BooleanField(required=False, default=False)
