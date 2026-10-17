from rest_framework import serializers


class CurrentUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.SerializerMethodField()

    def get_name(self, user):
        return user.first_name or user.username
