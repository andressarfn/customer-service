from dataclasses import dataclass

from loguru import logger

from src.application.use_cases.favorite.exceptions import (
    FavoriteProductAlreadyExistsError,
    FavoriteProductNotFoundError,
)
from src.domain.entities.favorite_entity import (
    FavoriteInputEntity,
    FavoriteOutputEntity,
)
from src.domain.repositories.favorite_repository_interface import (
    FavoriteRepositoryInterface,
)
from src.infrastructure.external_services.products.product_client import (
    ProductClientInterface,
)


@dataclass(frozen=True)
class AddFavoriteUseCase:
    favorite_repository: FavoriteRepositoryInterface
    product_client: ProductClientInterface

    async def execute(self, favorite_entity: FavoriteInputEntity) -> int:
        logger.info(
            f"Adding favorite item for customer_id: {favorite_entity.customer_id}, product_id: {favorite_entity.product_id}"
        )
        if not await self._check_product_exists(favorite_entity.product_id):
            logger.error(f"Product with id {favorite_entity.product_id} not found.")
            raise FavoriteProductNotFoundError(
                title="Product not found",
                detail=f"Product with id {favorite_entity.product_id} not found.",
                status_code=400,
            )
        if await self._check_favorite_exists(
            favorite_entity.customer_id, favorite_entity.product_id
        ):
            logger.error(
                f"Favorite item with product_id: {favorite_entity.product_id} already exists "
                f"for customer_id: {favorite_entity.customer_id}"
            )
            raise FavoriteProductAlreadyExistsError(
                title="Favorite already exists",
                detail=f"Favorite item with product_id: {favorite_entity.product_id} already exists "
                f"for customer_id: {favorite_entity.customer_id}",
                status_code=400,
            )

        result = await self.favorite_repository.add_favorite(
            favorite_entity.customer_id, favorite_entity.product_id
        )
        logger.info(
            f"Favorite product_id: {favorite_entity.product_id} added for customer_id: "
            f"{favorite_entity.customer_id}, item_id: {result}"
        )
        return FavoriteOutputEntity(product_id=favorite_entity.product_id)

    async def _check_product_exists(self, product_id: int) -> bool:
        return await self.product_client.get_product_by_id(product_id) is not None

    async def _check_favorite_exists(self, customer_id: int, product_id: int) -> bool:
        return await self.favorite_repository.favorite_exists_for_customer(
            customer_id, product_id
        )
