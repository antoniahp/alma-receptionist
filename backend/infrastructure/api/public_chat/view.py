import uuid

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from application.commands.handle_chat_button.command import HandleChatButtonCommand
from application.commands.handle_chat_button.command_dto import HandleChatButtonCommandDTO
from application.commands.handle_chat_message.command import HandleChatMessageCommand
from application.commands.handle_chat_message.command_dto import HandleChatMessageCommandDTO
from application.commands.start_chat.command import StartChatCommand
from application.commands.start_chat.command_dto import StartChatCommandDTO
from domain.entities import Conversation
from infrastructure import dependencies
from infrastructure.api.public_chat.serializer import PublicChatSerializer
from infrastructure.api.shared.serializers import ChatReplySerializer


class PublicChatView(APIView):
    """Chat de la web con la misma recepcionista que el bot de Telegram."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "chat"

    def post(self, request):
        serializer = PublicChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        session = str(data.get("session") or uuid.uuid4())
        key = f"{Conversation.WEB_PREFIX}{session}"

        if data["start"]:
            reply = StartChatCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
                StartChatCommandDTO(conversation_key=key)
            )
        elif data["button"]:
            reply = HandleChatButtonCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
                HandleChatButtonCommandDTO(conversation_key=key, data=data["button"])
            )
        else:
            reply = HandleChatMessageCommand(
                dependencies.get_repositories(), dependencies.get_message_service(), dependencies.get_language_model_service()
            ).execute(HandleChatMessageCommandDTO(conversation_key=key, text=data["message"]))

        last_message = dependencies.get_repositories().conversations.last_message_for_key(key)
        response = ChatReplySerializer(reply).data
        response["session"] = session
        response["last_id"] = str(last_message.id) if last_message else None
        return Response(response)
