from dataclasses import dataclass

from src.domain.entities.favorite_entity import (
    FavoritesOutputEntity,
    ProductFavoriteEntity,
)
from src.domain.repositories.favorite_repository_interface import (
    FavoriteRepositoryInterface,
)
from src.infrastructure.external_services.products.product_client import (
    ProductClientInterface,
)


@dataclass(frozen=True)
class GetFavoriteUseCase:
    favorite_repository: FavoriteRepositoryInterface
    product_client: ProductClientInterface

    async def execute(self, customer_id: int) -> list[ProductFavoriteEntity]:
        product_ids = await self.favorite_repository.get_favorites_by_customer_id(
            customer_id
        )
        products = []
        for product in product_ids:
            product = await self.product_client.get_product_by_id(product)
            if product:
                products.append(product)

        return FavoritesOutputEntity(
            customer_id=customer_id,
            favorites=products,
        )
