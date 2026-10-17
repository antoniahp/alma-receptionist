from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructure.api.current_user.serializer import CurrentUserSerializer


class CurrentUserView(APIView):
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)
