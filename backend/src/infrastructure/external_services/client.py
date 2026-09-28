from abc import ABC, abstractmethod

from httpx import AsyncClient, HTTPError, HTTPStatusError
from loguru import logger

from src.infrastructure.external_services.exceptions import ClientException


class ClientInterface(ABC):
    @abstractmethod
    async def get_by_path(self, url: str, headers: dict, timeout: int) -> dict: ...

    @abstractmethod
    async def get_by_query(
        self, url: str, headers: dict, params: dict, timeout: int
    ) -> dict: ...


class Client(ClientInterface):
    async def get_by_path(self, url: str, headers: dict, timeout: int = 10) -> dict:
        logger.info(f"GET by path to {url} with timeout {timeout}")
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response.json()
        except HTTPError as e:
            logger.error("HTTP error occurred while making GET by path request")
            logger.error(f"Response body: {e.response.text}")
            raise ClientException(
                title="HTTP error occurred",
                detail=str(e),
                status_code=(
                    e.response.status_code if isinstance(e, HTTPStatusError) else 500
                ),
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise e

    async def get_by_query(
        self, url: str, headers: dict, params: dict, timeout: int = 10
    ) -> dict:
        logger.info(f"GET by query to {url} with params {params} and timeout {timeout}")
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response.json()
        except HTTPError as e:
            logger.error("HTTP error occurred while making GET by query request")
            logger.error(f"Response body: {e.response.text}")
            raise ClientException(
                title="HTTP error occurred",
                detail=str(e),
                status_code=(
                    e.response.status_code if isinstance(e, HTTPStatusError) else 500
                ),
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise e
