from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.update_service.command import UpdateServiceCommand
from application.commands.update_service.command_dto import UpdateServiceCommandDTO
from infrastructure import dependencies
from infrastructure.api.service_detail.serializer import ServiceFormSerializer
from infrastructure.api.services.serializer import ServiceSerializer


class ServiceDetailView(APIView):
    def patch(self, request, service_id):
        serializer = ServiceFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = UpdateServiceCommand(dependencies.get_repositories()).execute(
            UpdateServiceCommandDTO(service_id=service_id, **serializer.validated_data)
        )
        return Response(ServiceSerializer(service).data)
