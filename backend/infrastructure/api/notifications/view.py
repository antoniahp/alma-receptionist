from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.list_notifications.query import ListNotificationsQuery
from application.queries.list_notifications.query_dto import ListNotificationsQueryDTO
from infrastructure import dependencies
from infrastructure.api.notifications.serializer import NotificationSerializer


class NotificationListView(APIView):
    def get(self, request):
        notifications = ListNotificationsQuery(dependencies.get_repositories()).execute(ListNotificationsQueryDTO())
        return Response(NotificationSerializer(notifications, many=True).data)
