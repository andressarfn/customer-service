import traceback
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.favorite_dto import FavoriteInputDTO
from src.application.mappers.favorite_mapper import FavoriteMapper
from src.application.use_cases.favorite.add import AddFavoriteUseCase
from src.application.use_cases.favorite.exceptions import (
    FavoriteProductAlreadyExistsError,
    FavoriteProductNotFoundError,
)
from src.application.use_cases.favorite.get import GetFavoriteUseCase
from src.infrastructure.database.postgres_client import PostgresConnectionClient
from src.infrastructure.external_services.products.product_client import (
    ProductClientInterface,
)
from src.infrastructure.repositories.favorite_repository import FavoriteRepository
from src.interfaces.api.auth.dependencies import get_current_user
from src.interfaces.api.v1.favorite.dependencies import get_product_client
from src.interfaces.api.v1.favorite.exceptions import (
    GetFavoriteException,
    PostFavoriteException,
)
from src.interfaces.api.v1.favorite.schema import (
    FavoriteRequestSchema,
    FavoriteResponseSchema,
    FavoritesResponseSchema,
)

favorite_v1_router = APIRouter(
    prefix="/v1", tags=["Favorite"], dependencies=[Depends(get_current_user)]
)


@favorite_v1_router.post(
    "/customer/{customer_id}/favorite",
    description="Add a favorite item for a customer",
    status_code=status.HTTP_201_CREATED,
    response_model=FavoriteResponseSchema,
)
async def add_favorite(
    customer_id: Annotated[int, Path(..., description="Customer ID")],
    schema: Annotated[FavoriteRequestSchema, Body(..., description="Favorite Item")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
    product_client: Annotated[ProductClientInterface, Depends(get_product_client)],
):
    try:
        favorite_input_dto = FavoriteInputDTO(
            customer_id=customer_id, product_id=schema.product_id
        )
        favorite_input_entity = FavoriteMapper.to_entity(favorite_input_dto)
        use_case = AddFavoriteUseCase(
            favorite_repository=FavoriteRepository(session),
            product_client=product_client,
        )
        favorite_output_entity = await use_case.execute(favorite_input_entity)
        return FavoriteResponseSchema(**favorite_output_entity.model_dump())
    except (FavoriteProductNotFoundError, FavoriteProductAlreadyExistsError) as e:
        raise e
    except Exception as e:
        raise PostFavoriteException(
            title="Failed to add favorite",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )


@favorite_v1_router.get(
    "/customer/{customer_id}/favorites",
    description="Get all favorite items for a customer",
    status_code=status.HTTP_200_OK,
    response_model=FavoritesResponseSchema,
)
async def get_favorites(
    customer_id: Annotated[int, Path(..., description="Customer ID")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
    product_client: Annotated[ProductClientInterface, Depends(get_product_client)],
):
    try:
        use_case = GetFavoriteUseCase(
            favorite_repository=FavoriteRepository(session),
            product_client=product_client,
        )
        favorites_output_entity = await use_case.execute(customer_id)
        return FavoritesResponseSchema(
            **favorites_output_entity.model_dump(),
        )
    except Exception as e:
        raise GetFavoriteException(
            title="Failed to get favorites",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )
