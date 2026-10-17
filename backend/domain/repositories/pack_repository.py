from abc import ABC, abstractmethod


class PackRepository(ABC):
    @abstractmethod
    def create(self, client, service, sessions_total, price, payment_method, sold_at):
        pass

    @abstractmethod
    def get_for_update(self, pack_id):
        pass

    @abstractmethod
    def find_active_for_update(self, client_id, service_id):
        """El bono más antiguo con sesiones de esa clienta para ese servicio, bloqueado para gastarlo; o None."""

    @abstractmethod
    def list_for_client(self, client_id):
        pass

    @abstractmethod
    def list_sold_between(self, start, end):
        pass

    @abstractmethod
    def active_pairs(self, client_ids):
        """Conjunto de (client_id, service_id) que tienen un bono con sesiones."""

    @abstractmethod
    def save(self, pack, fields):
        pass
