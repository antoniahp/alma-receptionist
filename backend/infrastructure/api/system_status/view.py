from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_system_status.query import GetSystemStatusQuery
from application.queries.get_system_status.query_dto import GetSystemStatusQueryDTO
from infrastructure import dependencies
from infrastructure.api.system_status.serializer import SystemStatusSerializer


class SystemStatusView(APIView):
    def get(self, request):
        status = GetSystemStatusQuery(dependencies.get_language_model_service(), dependencies.get_message_service()).execute(
            GetSystemStatusQueryDTO()
        )
        return Response(SystemStatusSerializer(status).data)
