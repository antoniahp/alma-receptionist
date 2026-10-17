from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.cancel_appointment.command import CancelAppointmentCommand
from application.commands.cancel_appointment.command_dto import CancelAppointmentCommandDTO
from application.commands.complete_appointment.command import CompleteAppointmentCommand
from application.commands.complete_appointment.command_dto import CompleteAppointmentCommandDTO
from application.commands.mark_no_show.command import MarkNoShowCommand
from application.commands.mark_no_show.command_dto import MarkNoShowCommandDTO
from application.commands.send_reminder.command import SendReminderCommand
from application.commands.send_reminder.command_dto import SendReminderCommandDTO
from application.commands.undo_complete_appointment.command import UndoCompleteAppointmentCommand
from application.commands.undo_complete_appointment.command_dto import UndoCompleteAppointmentCommandDTO
from infrastructure import dependencies
from infrastructure.api.appointment_actions.serializer import CompleteAppointmentSerializer, CompletedAppointmentSerializer
from infrastructure.api.shared.serializers import AppointmentSerializer, NotificationSerializer


class CompleteAppointmentView(APIView):
    def post(self, request, appointment_id):
        serializer = CompleteAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment, used = CompleteAppointmentCommand(dependencies.get_repositories()).execute(
            CompleteAppointmentCommandDTO(appointment_id=appointment_id, payment_method=serializer.validated_data["payment_method"])
        )
        return Response(CompletedAppointmentSerializer({"appointment": appointment, "used": used}).data)


class UndoCompleteAppointmentView(APIView):
    def post(self, request, appointment_id):
        appointment = UndoCompleteAppointmentCommand(dependencies.get_repositories()).execute(
            UndoCompleteAppointmentCommandDTO(appointment_id=appointment_id)
        )
        return Response(AppointmentSerializer(appointment).data)


class CancelAppointmentView(APIView):
    def post(self, request, appointment_id):
        appointment = CancelAppointmentCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
            CancelAppointmentCommandDTO(appointment_id=appointment_id)
        )
        return Response(AppointmentSerializer(appointment).data)


class NoShowAppointmentView(APIView):
    def post(self, request, appointment_id):
        appointment = MarkNoShowCommand(dependencies.get_repositories()).execute(MarkNoShowCommandDTO(appointment_id=appointment_id))
        return Response(AppointmentSerializer(appointment).data)


class RemindAppointmentView(APIView):
    def post(self, request, appointment_id):
        notification = SendReminderCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
            SendReminderCommandDTO(appointment_id=appointment_id)
        )
        return Response(NotificationSerializer(notification).data)
