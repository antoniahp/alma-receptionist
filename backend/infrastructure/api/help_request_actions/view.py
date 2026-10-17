from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.answer_help_request.command import AnswerHelpRequestCommand
from application.commands.answer_help_request.command_dto import AnswerHelpRequestCommandDTO
from application.commands.close_help_request.command import CloseHelpRequestCommand
from application.commands.close_help_request.command_dto import CloseHelpRequestCommandDTO
from infrastructure import dependencies
from infrastructure.api.help_request_actions.serializer import AnswerHelpRequestSerializer
from infrastructure.api.help_requests.serializer import HelpRequestSerializer


class AnswerHelpRequestView(APIView):
    def post(self, request, help_request_id):
        serializer = AnswerHelpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        help_request = AnswerHelpRequestCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
            AnswerHelpRequestCommandDTO(
                help_request_id=help_request_id,
                text=serializer.validated_data["text"],
                sign_as_owner=serializer.validated_data["sign"],
            )
        )
        return Response(HelpRequestSerializer(help_request).data)


class CloseHelpRequestView(APIView):
    def post(self, request, help_request_id):
        help_request = CloseHelpRequestCommand(dependencies.get_repositories()).execute(
            CloseHelpRequestCommandDTO(help_request_id=help_request_id)
        )
        return Response(HelpRequestSerializer(help_request).data)
