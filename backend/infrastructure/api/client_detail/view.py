from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.update_client.command import UpdateClientCommand
from application.commands.update_client.command_dto import UpdateClientCommandDTO
from application.queries.get_client_file.query import GetClientFileQuery
from application.queries.get_client_file.query_dto import GetClientFileQueryDTO
from infrastructure import dependencies
from infrastructure.api.client_detail.serializer import ClientFileSerializer, UpdateClientSerializer
from infrastructure.api.shared.serializers import ClientSerializer


class ClientDetailView(APIView):
    def get(self, request, client_id):
        """Ficha de la clienta: datos, historial de citas y bonos."""
        client_file = GetClientFileQuery(dependencies.get_repositories()).execute(GetClientFileQueryDTO(client_id=client_id))
        return Response(ClientFileSerializer(client_file).data)

    def patch(self, request, client_id):
        serializer = UpdateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = UpdateClientCommand(dependencies.get_repositories()).execute(
            UpdateClientCommandDTO(client_id=client_id, **serializer.validated_data)
        )
        return Response(ClientSerializer(client).data)
