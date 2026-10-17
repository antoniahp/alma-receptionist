from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.list_conversations.query import ListConversationsQuery
from application.queries.list_conversations.query_dto import ListConversationsQueryDTO
from infrastructure import dependencies
from infrastructure.api.conversations.serializer import ConversationSerializer


class ConversationListView(APIView):
    def get(self, request):
        conversations = ListConversationsQuery(dependencies.get_repositories()).execute(ListConversationsQueryDTO())
        return Response(ConversationSerializer(conversations, many=True).data)
