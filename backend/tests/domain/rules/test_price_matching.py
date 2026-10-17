import pytest
from types import SimpleNamespace

from domain.rules.price_matching import is_same_product, is_second_hand, supplier_for_store


def test_same_product_written_differently():
    assert is_same_product(
        "OPI GelColor esmalte semipermanente 15 ml", "OPI GelColor Intelli-Gel esmalte semipermanente 15ml Big Apple Red"
    )


def test_other_brand_is_not_the_same_product():
    assert not is_same_product("Germaine de Capuccini contorno de ojos", "Ziaja Crema Contorno de Ojos Antiojeras con Aciano")


def test_sizes_do_not_count():
    assert is_same_product("Starpil cera tibia natural 800 ml", "Cera tibia natural Starpil lata")


def test_a_smaller_size_is_another_product():
    assert not is_same_product(
        "La Roche-Posay Cicaplast Baume B5 100 ml", "La Roche-Posay, Cicaplast Baume B5+, Bálsamo Calmante Reparador, 40 ml"
    )
    assert is_same_product("La Roche-Posay Cicaplast Baume B5 100 ml", "La Roche Posay Cicaplast Baume B5 100ml")


def test_second_hand_shops_are_detected():
    assert is_second_hand("Wallapop")
    assert not is_second_hand("Farmacia Imperial")


def test_supplier_for_store():
    germaine = SimpleNamespace(name="Germaine de Capuccini")
    opi = SimpleNamespace(name="OPI")

    assert supplier_for_store([opi, germaine], "Germaine de Capuccini") == germaine
    assert supplier_for_store([opi, germaine], "Druni") is None


@pytest.mark.parametrize(
    "offer_title",
    [
        "Lifting Pestañas Kit, 2026 Kit de Levantamiento de Pestañas",  # otra marca
        "Refectocil Beautylash Brow Lift Kit lifting cejas",  # cejas, no pestañas
    ],
)
def test_another_brand_or_another_product_is_not_cheaper(offer_title):
    assert not is_same_product("Refectocil kit lifting de pestañas", offer_title)


def test_the_same_product_with_more_words_in_the_shop_still_matches():
    assert is_same_product("Refectocil kit lifting de pestañas", "Refectocil Kit Lifting de Pestañas 36 aplicaciones")
