from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.close_cash.command import CloseCashCommand
from application.commands.close_cash.command_dto import CloseCashCommandDTO
from application.queries.get_cash_day.query import GetCashDayQuery
from application.queries.get_cash_day.query_dto import GetCashDayQueryDTO
from infrastructure import dependencies
from infrastructure.api.cash_day.serializer import CashDayParamsSerializer, CashDaySerializer, CloseCashSerializer


class CashDayView(APIView):
    def get(self, request):
        params = CashDayParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        day = params.validated_data.get("day") or timezone.localdate()
        return Response(CashDaySerializer(GetCashDayQuery(dependencies.get_repositories()).execute(GetCashDayQueryDTO(day=day))).data)

    def post(self, request):
        serializer = CloseCashSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repositories = dependencies.get_repositories()
        CloseCashCommand(repositories).execute(CloseCashCommandDTO(**serializer.validated_data))
        day = serializer.validated_data["day"]
        return Response(CashDaySerializer(GetCashDayQuery(repositories).execute(GetCashDayQueryDTO(day=day))).data)
