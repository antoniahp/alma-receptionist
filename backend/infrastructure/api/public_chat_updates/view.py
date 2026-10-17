from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from application.queries.get_chat_updates.query import GetChatUpdatesQuery
from application.queries.get_chat_updates.query_dto import GetChatUpdatesQueryDTO
from infrastructure import dependencies
from infrastructure.api.public_chat_updates.serializer import ChatUpdateSerializer, ChatUpdatesFiltersSerializer


class PublicChatUpdatesView(APIView):
    """El chat web pregunta cada pocos segundos si la dueña ha contestado algo."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "chat_updates"

    def get(self, request):
        filters = ChatUpdatesFiltersSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        messages = GetChatUpdatesQuery(dependencies.get_repositories()).execute(
            GetChatUpdatesQueryDTO(session=str(filters.validated_data["session"]), after_message_id=filters.validated_data["after"])
        )
        return Response(ChatUpdateSerializer(messages, many=True).data)
