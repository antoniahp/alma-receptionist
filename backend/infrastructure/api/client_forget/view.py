from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.forget_client.command import ForgetClientCommand
from application.commands.forget_client.command_dto import ForgetClientCommandDTO
from infrastructure import dependencies
from infrastructure.api.shared.serializers import ClientSerializer


class ForgetClientView(APIView):
    def post(self, request, client_id):
        """La clienta ha pedido que se borren sus datos (RGPD)."""
        client = ForgetClientCommand(dependencies.get_repositories()).execute(ForgetClientCommandDTO(client_id=client_id))
        return Response(ClientSerializer(client).data)
