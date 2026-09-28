from abc import ABC, abstractmethod
from dataclasses import dataclass

from loguru import logger

from src.infrastructure.config.settings import settings
from src.infrastructure.external_services.client import ClientInterface


class ProductClientInterface(ABC):
    @abstractmethod
    async def get_product_by_id(self, product_id: int) -> dict | None: ...

    @abstractmethod
    async def get_list_products(self) -> list[dict]: ...


@dataclass(frozen=True)
class ProductClient(ProductClientInterface):
    client: ClientInterface

    async def get_product_by_id(self, product_id: int) -> dict | None:
        logger.info(f"Fetching product with id {product_id} from external service")
        url = f"{settings.PRODUCT_CLIENT_URL}/api/product/{product_id}"
        headers = {
            "Content-Type": "application/json",
        }
        response = await self.client.get_by_path(url=url, headers=headers)
        logger.info(f"Response from product service: {response}")
        return response

    async def get_list_products(self) -> list[dict]:
        logger.info("Fetching product list from external service")
        products = []
        page = 1
        while True:
            url = f"{settings.PRODUCT_CLIENT_URL}/api/product/"
            headers = {
                "Content-Type": "application/json",
            }
            params = {"page": page}
            response = await self.client.get_by_query(
                url=url, headers=headers, params=params
            )
            logger.info(
                f"Response from product service page: {page} "
                f"with count: {response.get('count', 0)}"
            )
            if not response or not response.get("results"):
                break
            products.extend(response["results"])
            if not response.get("next"):
                break
            page += 1
        return products
