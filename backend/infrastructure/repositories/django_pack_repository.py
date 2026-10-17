from django.db.models import F

from domain.entities import ClientPack
from domain.repositories.pack_repository import PackRepository


class DjangoPackRepository(PackRepository):
    def create(self, client, service, sessions_total, price, payment_method, sold_at):
        return ClientPack.objects.create(
            client=client, service=service, sessions_total=sessions_total, price=price, payment_method=payment_method, sold_at=sold_at
        )

    def get_for_update(self, pack_id):
        return ClientPack.objects.select_for_update().get(pk=pack_id)

    def find_active_for_update(self, client_id, service_id):
        packs = ClientPack.objects.select_for_update().filter(
            client_id=client_id, service_id=service_id, sessions_used__lt=F("sessions_total")
        )
        return packs.order_by("sold_at").first()

    def list_for_client(self, client_id):
        return list(ClientPack.objects.select_related("service").filter(client_id=client_id))

    def list_sold_between(self, start, end):
        return list(ClientPack.objects.select_related("client", "service").filter(sold_at__gte=start, sold_at__lt=end))

    def active_pairs(self, client_ids):
        packs = ClientPack.objects.filter(client_id__in=client_ids, sessions_used__lt=F("sessions_total"))
        return set(packs.values_list("client_id", "service_id"))

    def save(self, pack, fields):
        pack.save(update_fields=fields)
