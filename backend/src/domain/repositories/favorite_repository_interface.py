from abc import ABC, abstractmethod


class FavoriteRepositoryInterface(ABC):
    @abstractmethod
    async def favorite_exists_for_customer(
        self, customer_id: int, product_id: str
    ) -> bool: ...

    @abstractmethod
    async def add_favorite(self, customer_id: int, favorite_item: str) -> None: ...

    @abstractmethod
    async def get_favorites_by_customer_id(self, customer_id: int) -> list[str]: ...
