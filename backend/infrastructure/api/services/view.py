from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.create_service.command import CreateServiceCommand
from application.commands.create_service.command_dto import CreateServiceCommandDTO
from application.queries.list_services.query import ListServicesQuery
from application.queries.list_services.query_dto import ListServicesQueryDTO
from infrastructure import dependencies
from infrastructure.api.service_detail.serializer import ServiceFormSerializer
from infrastructure.api.services.serializer import ServiceSerializer


class ServiceListView(APIView):
    def get(self, request):
        services = ListServicesQuery(dependencies.get_repositories()).execute(ListServicesQueryDTO())
        return Response(ServiceSerializer(services, many=True).data)

    def post(self, request):
        serializer = ServiceFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {key: value for key, value in serializer.validated_data.items() if key != "active"}
        service = CreateServiceCommand(dependencies.get_repositories()).execute(CreateServiceCommandDTO(**data))
        return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)
