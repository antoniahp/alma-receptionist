from application.queries.get_store_link.query import GetStoreLinkQuery
from application.queries.get_store_link.query_dto import GetStoreLinkQueryDTO
from domain.exceptions import InvalidShoppingListItem, PriceSearchUnavailable


class AddToShoppingListCommand:
    """La dueña elige una oferta del comparador (la más barata o la que prefiera) para comprarla.

    Se guarda el enlace directo a la tienda para poder comprarlo luego en un clic.
    """

    def __init__(self, repositories, price_search_service):
        self.repositories = repositories
        self.price_search_service = price_search_service

    def execute(self, dto):
        if dto.units < 1 or dto.price < 0 or not dto.store.strip():
            raise InvalidShoppingListItem()
        product = self.repositories.products.get(dto.product_id)
        return self.repositories.shopping_list.add_or_update(
            product=product,
            store=dto.store.strip()[:120],
            title=dto.title.strip()[:300],
            price=dto.price,
            link=self.direct_link(dto)[:2000],
            units=dto.units,
        )

    def direct_link(self, dto):
        """El de la tienda si se puede; si no, el de Google Shopping que ya teníamos."""
        if not dto.page_token or not self.price_search_service.is_enabled():
            return dto.link
        try:
            link = GetStoreLinkQuery(self.price_search_service, self.repositories).execute(
                GetStoreLinkQueryDTO(page_token=dto.page_token, store=dto.store)
            )
            return link or dto.link
        except PriceSearchUnavailable:
            return dto.link
