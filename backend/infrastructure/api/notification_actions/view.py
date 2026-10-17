from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.send_due_notifications.command import SendDueNotificationsCommand
from application.commands.send_due_notifications.command_dto import SendDueNotificationsCommandDTO
from application.commands.send_reactivation.command import SendReactivationCommand
from application.commands.send_reactivation.command_dto import SendReactivationCommandDTO
from infrastructure import dependencies
from infrastructure.api.notification_actions.serializer import SendReactivationSerializer, SentCountSerializer
from infrastructure.api.shared.serializers import NotificationSerializer


class SendDueNotificationsView(APIView):
    def post(self, request):
        sent = SendDueNotificationsCommand(
            dependencies.get_repositories(), dependencies.get_message_service(), dependencies.get_language_model_service()
        ).execute(SendDueNotificationsCommandDTO())
        return Response(SentCountSerializer(sent).data)


class SendReactivationView(APIView):
    def post(self, request):
        serializer = SendReactivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = SendReactivationCommand(
            dependencies.get_repositories(), dependencies.get_message_service(), dependencies.get_language_model_service()
        ).execute(
            SendReactivationCommandDTO(client_id=serializer.validated_data["client"], service_id=serializer.validated_data["service"])
        )
        return Response(NotificationSerializer(notification).data)
