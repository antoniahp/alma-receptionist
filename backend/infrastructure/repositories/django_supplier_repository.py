from domain.entities import Supplier
from domain.repositories.supplier_repository import SupplierRepository


class DjangoSupplierRepository(SupplierRepository):
    def get(self, supplier_id):
        return Supplier.objects.get(pk=supplier_id)

    def save(self, supplier, fields):
        supplier.save(update_fields=fields)

    def list(self):
        return list(Supplier.objects.all())

    def create(self, name):
        return Supplier.objects.create(name=name[:120])
