"""Demo pública: no se envían correos de verdad y la pantalla de entrada enseña el usuario de prueba."""

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command

from infrastructure.services.demo_email_service import DemoEmailService

pytestmark = pytest.mark.django_db


def test_the_demo_email_service_never_sends_anything():
    DemoEmailService().send("pedidos@proveedor.com", "Pedido", "Hola")

    assert mail.outbox == []


def test_public_info_shows_the_demo_login_only_in_demo_mode(api_client, settings):
    assert api_client.get("/api/public/info/").json()["demo_login"] is None

    settings.DEMO_MODE = True
    settings.DEMO_USERNAME = "demo"
    settings.DEMO_PASSWORD = "demo1234"

    assert api_client.get("/api/public/info/").json()["demo_login"] == {"username": "demo", "password": "demo1234"}


def test_demo_hints_can_be_hidden_while_the_demo_keeps_working(api_client, settings):
    settings.DEMO_MODE = True
    settings.DEMO_HINTS = False

    assert api_client.get("/api/public/info/").json()["demo_login"] is None
    DemoEmailService().send("pedidos@proveedor.com", "Pedido", "Hola")
    assert mail.outbox == []


def test_seed_creates_the_demo_user(settings):
    settings.DEMO_MODE = True
    settings.DEMO_USERNAME = "demo"
    settings.DEMO_PASSWORD = "demo1234"

    call_command("seed_demo", stdout=open("/dev/null", "w"))

    assert get_user_model().objects.get(username="demo").check_password("demo1234")
