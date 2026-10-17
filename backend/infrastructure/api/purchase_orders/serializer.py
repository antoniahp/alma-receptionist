from rest_framework import serializers


class UpdateOrderDraftSerializer(serializers.Serializer):
    email_subject = serializers.CharField(max_length=200, allow_blank=True)
    email_body = serializers.CharField(allow_blank=True)
