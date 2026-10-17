from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.sell_pack.command import SellPackCommand
from application.commands.sell_pack.command_dto import SellPackCommandDTO
from infrastructure import dependencies
from infrastructure.api.packs.serializer import SellPackSerializer
from infrastructure.api.shared.serializers import PackSerializer


class PackListView(APIView):
    def post(self, request):
        serializer = SellPackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        pack = SellPackCommand(dependencies.get_repositories()).execute(
            SellPackCommandDTO(
                client_id=data["client"],
                service_id=data["service"],
                sessions=data["sessions"],
                price=data["price"],
                payment_method=data["payment_method"],
            )
        )
        return Response(PackSerializer(pack).data, status=status.HTTP_201_CREATED)
