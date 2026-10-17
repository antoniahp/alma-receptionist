from types import SimpleNamespace

from domain.rules.store_trust import amazon_cart_link, is_trusted_link, is_trusted_store

GERMAINE = SimpleNamespace(name="Germaine de Capuccini")


def test_known_stores_and_brand_websites_are_trusted():
    assert is_trusted_store("Amazon.es", [])
    assert is_trusted_store("AliExpress - Tienda 123", [])
    assert is_trusted_store("Druni", [])
    assert is_trusted_store("Germaine de Capuccini", [GERMAINE])
    assert not is_trusted_store("Estéticas Pasco", [GERMAINE])


def test_links_must_be_on_the_store_domain():
    assert is_trusted_link("Druni", "https://www.druni.es/cicaplast", [])
    assert not is_trusted_link("Druni", "https://druni.es.ofertas.example/cicaplast", [])
    assert not is_trusted_link("Druni", "http://www.druni.es/cicaplast", [])
    assert is_trusted_link("Germaine de Capuccini", "https://www.germaine-de-capuccini.com/es/purexpert", [GERMAINE])


def test_amazon_cart_link_with_all_the_products():
    link = amazon_cart_link([("https://www.amazon.es/dp/B0ABCDEF12", 2), ("https://www.amazon.es/Crema-X/dp/B0XYZ12345?th=1", 1)])

    assert link == "https://www.amazon.es/gp/aws/cart/add.html?ASIN.1=B0ABCDEF12&Quantity.1=2&ASIN.2=B0XYZ12345&Quantity.2=1"


def test_amazon_cart_link_needs_product_codes():
    assert amazon_cart_link([("https://www.google.com/search?ibp=oshop", 1)]) == ""
