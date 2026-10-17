from domain.entities import HelpRequest
from domain.repositories.help_request_repository import HelpRequestRepository


class DjangoHelpRequestRepository(HelpRequestRepository):
    def base_queryset(self):
        return HelpRequest.objects.select_related("client", "conversation")

    def get(self, help_request_id):
        return self.base_queryset().get(pk=help_request_id)

    def find_open_for_conversation(self, conversation):
        return self.base_queryset().filter(conversation=conversation, status=HelpRequest.OPEN).first()

    def find_by_owner_message_id(self, message_id):
        if not message_id:
            return None
        return self.base_queryset().filter(owner_message_id=str(message_id)).first()

    def create(self, conversation, client, question, contact):
        return HelpRequest.objects.create(conversation=conversation, client=client, question=question, contact=contact)

    def save(self, help_request, fields):
        help_request.save(update_fields=fields)

    def list(self, statuses=None, limit=50):
        help_requests = self.base_queryset()
        if statuses:
            help_requests = help_requests.filter(status__in=statuses)
        return list(help_requests[:limit])

    def last_open(self):
        return self.base_queryset().filter(status=HelpRequest.OPEN).order_by("-created_at").first()

    def count_open(self):
        return HelpRequest.objects.filter(status=HelpRequest.OPEN).count()
