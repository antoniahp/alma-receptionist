from django.utils import timezone

from domain.entities import HelpRequest


class CloseHelpRequestCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        help_request = self.repositories.help_requests.get(dto.help_request_id)
        help_request.status = HelpRequest.CLOSED
        if help_request.answered_at is None:
            help_request.answered_at = timezone.now()
        self.repositories.help_requests.save(help_request, ["status", "answered_at"])
        return help_request
