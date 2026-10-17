import pytest

from domain.entities import PushSubscription

pytestmark = pytest.mark.django_db

SUBSCRIPTION = {"endpoint": "https://push.example/navegador", "keys": {"p256dh": "clave", "auth": "secreto"}}


def test_subscribe_sends_a_test_alert_and_unsubscribe(owner_client, fake_services):
    assert owner_client.get("/api/push/").json() == {"enabled": True, "public_key": "clave-publica"}

    assert owner_client.post("/api/push/", SUBSCRIPTION, format="json").status_code == 201
    assert fake_services["push_service"].sent[0]["title"] == "🔔 Avisos activados"

    owner_client.delete("/api/push/", {"endpoint": SUBSCRIPTION["endpoint"]}, format="json")
    assert not PushSubscription.objects.exists()


def test_only_the_owner_can_subscribe(api_client):
    assert api_client.post("/api/push/", SUBSCRIPTION, format="json").status_code == 401
