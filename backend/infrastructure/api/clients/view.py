from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.create_client.command import CreateClientCommand
from application.commands.create_client.command_dto import CreateClientCommandDTO
from application.queries.list_clients.query import ListClientsQuery
from application.queries.list_clients.query_dto import ListClientsQueryDTO
from infrastructure import dependencies
from infrastructure.api.clients.serializer import CreateClientSerializer
from infrastructure.api.shared.serializers import ClientSerializer


class ClientListView(APIView):
    def get(self, request):
        clients = ListClientsQuery(dependencies.get_repositories()).execute(ListClientsQueryDTO(search=request.query_params.get("q", "")))
        return Response(ClientSerializer(clients, many=True).data)

    def post(self, request):
        serializer = CreateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = CreateClientCommand(dependencies.get_repositories()).execute(CreateClientCommandDTO(**serializer.validated_data))
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
