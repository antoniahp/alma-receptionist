from rest_framework import serializers


class LatestHelpRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    question = serializers.CharField()
    client_name = serializers.SerializerMethodField()

    def get_client_name(self, help_request):
        return help_request.client.name if help_request.client else ""


class DashboardSerializer(serializers.Serializer):
    appointments_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    reminders_due = serializers.IntegerField()
    reactivations_due = serializers.IntegerField()
    products_to_order = serializers.IntegerField()
    orders_to_approve = serializers.IntegerField()
    help_requests_open = serializers.IntegerField()
    latest_help_request = LatestHelpRequestSerializer(allow_null=True)
