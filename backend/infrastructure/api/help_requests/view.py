from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.list_help_requests.query import ListHelpRequestsQuery
from application.queries.list_help_requests.query_dto import ListHelpRequestsQueryDTO
from infrastructure import dependencies
from infrastructure.api.help_requests.serializer import HelpRequestSerializer


class HelpRequestListView(APIView):
    def get(self, request):
        status_param = request.query_params.get("status", "")
        statuses = [value for value in status_param.split(",") if value]
        help_requests = ListHelpRequestsQuery(dependencies.get_repositories()).execute(ListHelpRequestsQueryDTO(statuses=statuses))
        return Response(HelpRequestSerializer(help_requests, many=True).data)
