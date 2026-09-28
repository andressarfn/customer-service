from src.application.dtos.favorite_dto import FavoriteInputDTO
from src.domain.entities.favorite_entity import FavoriteInputEntity


class FavoriteMapper:
    @staticmethod
    def to_entity(dto: FavoriteInputDTO) -> FavoriteInputEntity:
        return FavoriteInputEntity(
            customer_id=dto.customer_id, product_id=dto.product_id
        )
