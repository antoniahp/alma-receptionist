from rest_framework import serializers


class LanguageModelStatusSerializer(serializers.Serializer):
    available = serializers.BooleanField()
    model = serializers.CharField()
    enabled = serializers.BooleanField()


class TelegramStatusSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    bot_username = serializers.CharField(allow_blank=True)
    owner_alerts = serializers.BooleanField()


class SystemStatusSerializer(serializers.Serializer):
    business = serializers.DictField()
    demo = serializers.BooleanField()
    llm = LanguageModelStatusSerializer()
    telegram = TelegramStatusSerializer()
