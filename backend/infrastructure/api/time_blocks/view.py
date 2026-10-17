from datetime import timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.create_time_block.command import CreateTimeBlockCommand
from application.commands.create_time_block.command_dto import CreateTimeBlockCommandDTO
from application.queries.list_time_blocks.query import ListTimeBlocksQuery
from application.queries.list_time_blocks.query_dto import ListTimeBlocksQueryDTO
from application.shared.schedule import start_of_day
from infrastructure import dependencies
from infrastructure.api.time_blocks.serializer import DaysRangeSerializer, TimeBlockSerializer


class TimeBlockListView(APIView):
    def get(self, request):
        """GET /api/blocks/?start=2026-10-16&end=2026-10-22 (ambos días incluidos)."""
        days = DaysRangeSerializer(data=request.query_params)
        days.is_valid(raise_exception=True)
        blocks = ListTimeBlocksQuery(dependencies.get_repositories()).execute(
            ListTimeBlocksQueryDTO(
                start=start_of_day(days.validated_data["start"]), end=start_of_day(days.validated_data["end"]) + timedelta(days=1)
            )
        )
        return Response(TimeBlockSerializer(blocks, many=True).data)

    def post(self, request):
        serializer = TimeBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        block = CreateTimeBlockCommand(dependencies.get_repositories()).execute(CreateTimeBlockCommandDTO(**serializer.validated_data))
        return Response(TimeBlockSerializer(block).data, status=status.HTTP_201_CREATED)
