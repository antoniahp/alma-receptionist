from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.delete_push_subscription.command import DeletePushSubscriptionCommand
from application.commands.delete_push_subscription.command_dto import DeletePushSubscriptionCommandDTO
from application.commands.save_push_subscription.command import SavePushSubscriptionCommand
from application.commands.save_push_subscription.command_dto import SavePushSubscriptionCommandDTO
from application.commands.send_owner_push.command import SendOwnerPushCommand
from application.commands.send_owner_push.command_dto import SendOwnerPushCommandDTO
from infrastructure import dependencies
from infrastructure.api.push_subscriptions.serializer import PushEndpointSerializer, PushSubscriptionSerializer


class PushSubscriptionView(APIView):
    def get(self, request):
        """Clave pública para suscribirse (vacía si el servidor no tiene configurados los avisos)."""
        push = dependencies.get_push_service()
        return Response({"enabled": push.is_enabled(), "public_key": push.public_key()})

    def post(self, request):
        serializer = PushSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        repositories = dependencies.get_repositories()
        SavePushSubscriptionCommand(repositories).execute(
            SavePushSubscriptionCommandDTO(endpoint=data["endpoint"], p256dh=data["keys"]["p256dh"], auth=data["keys"]["auth"])
        )
        # Un aviso de prueba para que la dueña vea al momento cómo le van a llegar
        SendOwnerPushCommand(repositories, dependencies.get_push_service()).execute(
            SendOwnerPushCommandDTO(title="🔔 Avisos activados", body="Así te avisaré cuando una clienta escriba o reserve.", url="/panel")
        )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        serializer = PushEndpointSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DeletePushSubscriptionCommand(dependencies.get_repositories()).execute(
            DeletePushSubscriptionCommandDTO(endpoint=serializer.validated_data["endpoint"])
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
