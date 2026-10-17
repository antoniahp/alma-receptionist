from django.core.exceptions import ValidationError

from domain.entities import Service, ServiceProduct
from domain.repositories.service_repository import ServiceRepository


class DjangoServiceRepository(ServiceRepository):
    def get(self, service_id):
        return Service.objects.get(pk=service_id)

    def find_active(self, service_id):
        if not service_id:
            return None
        try:
            return Service.objects.filter(pk=service_id, active=True).first()
        except ValidationError:
            return None

    def list(self, only_active=False):
        services = Service.objects.prefetch_related("consumption__product")
        if only_active:
            services = services.filter(active=True)
        return list(services)

    def list_consumption(self, service):
        return list(service.consumption.select_related("product"))

    def add_consumption(self, service, product, uses):
        ServiceProduct.objects.update_or_create(service=service, product=product, defaults={"uses": uses})

    def create(self, **fields):
        return Service.objects.create(**fields)

    def save(self, service, fields):
        service.save(update_fields=fields)
