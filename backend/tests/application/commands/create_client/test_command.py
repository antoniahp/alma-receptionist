import pytest

from application.commands.create_client.command import CreateClientCommand
from application.commands.create_client.command_dto import CreateClientCommandDTO
from application.commands.update_client.command import UpdateClientCommand
from application.commands.update_client.command_dto import UpdateClientCommandDTO
from domain.exceptions import DuplicatedClient, InvalidClientData
from domain.rules.phone_format import clean_phone

pytestmark = pytest.mark.django_db


def test_phone_is_always_written_the_same_way():
    assert clean_phone("600123456") == "600 123 456"
    assert clean_phone("600-12-34-56") == "600 123 456"
    assert clean_phone("+34 600 12 34 56") == "+34 600 123 456"


def test_owner_adds_a_client_by_hand(repositories, salon):
    client = CreateClientCommand(repositories).execute(
        CreateClientCommandDTO(name=" Rocío Martín ", phone="622334455", email="Rocio@Mail.com", notes="Piel sensible")
    )

    assert client.name == "Rocío Martín"
    assert client.phone == "622 334 455"
    assert client.email == "rocio@mail.com"


def test_the_same_phone_written_differently_is_detected(repositories, salon):
    with pytest.raises(DuplicatedClient, match="Laura"):
        CreateClientCommand(repositories).execute(CreateClientCommandDTO(name="Laura G.", phone="611 11 11 11"))


def test_bad_email_is_rejected(repositories, salon):
    with pytest.raises(InvalidClientData):
        CreateClientCommand(repositories).execute(CreateClientCommandDTO(name="Rocío", email="rocio@"))


def test_edit_a_client(repositories, salon):
    client = UpdateClientCommand(repositories).execute(
        UpdateClientCommandDTO(
            client_id=salon.laura.id,
            name="Laura Gómez Ruiz",
            phone="611111111",
            email="",
            notes="Alérgica al látex",
            accepts_reminders=False,
        )
    )

    salon.laura.refresh_from_db()
    assert salon.laura.name == "Laura Gómez Ruiz"
    assert salon.laura.notes == "Alérgica al látex"
    assert salon.laura.accepts_reminders is False
    assert client.phone == "611 111 111"
