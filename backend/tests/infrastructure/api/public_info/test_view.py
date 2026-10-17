import pytest
from model_bakery import baker

from domain.entities import Service

pytestmark = pytest.mark.django_db


def test_public_info_groups_services_by_category(api_client, salon):
    baker.make(Service, name="Depilación axilas", category=Service.WAXING, price=6, duration_minutes=10)
    baker.make(Service, name="Maquillaje de novia", category=Service.MAKEUP, price=45, duration_minutes=45, active=False)

    info = api_client.get("/api/public/info/").json()

    assert info["categories"] == [{"key": "facial", "label": "Facial"}, {"key": "depilacion", "label": "Depilación"}]
    assert {service["category"] for service in info["services"]} == {"facial", "depilacion"}
