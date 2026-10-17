from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.delete_time_block.command import DeleteTimeBlockCommand
from application.commands.delete_time_block.command_dto import DeleteTimeBlockCommandDTO
from infrastructure import dependencies


class TimeBlockDetailView(APIView):
    def delete(self, request, block_id):
        DeleteTimeBlockCommand(dependencies.get_repositories()).execute(DeleteTimeBlockCommandDTO(block_id=block_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
