from abc import ABC
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseConnectionClient(ABC):
    _async_engine: AsyncEngine
    _async_sessionmaker: async_sessionmaker

    @classmethod
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        if cls._async_sessionmaker is None:
            raise RuntimeError(
                f"{cls.__name__} has not been initialized. Call initialize() first."
            )

        async_session: AsyncSession
        async with cls._async_sessionmaker() as async_session:
            async with async_session.begin():
                try:
                    yield async_session
                except Exception as e:
                    logger.exception(
                        f"Exception while processing the database session: {e}"
                    )
                    await async_session.rollback()
                    raise

    @classmethod
    async def _create_engine(cls, connection_url: str, schema_name: str, debug: bool):
        logger.debug("Starting the database engine")

        cls._async_engine = create_async_engine(
            url=connection_url,
            connect_args={"server_settings": {"search_path": schema_name}},
            pool_pre_ping=True,
            echo=debug,
            future=True,
        )

        logger.debug("Connection engine created")

    @classmethod
    async def _create_session(cls):
        logger.info("Starting the database session maker")

        cls._async_sessionmaker = async_sessionmaker(
            bind=cls._async_engine,
            expire_on_commit=False,
            autocommit=False,
        )

        logger.info("Connection session created")

    @classmethod
    async def _ping(cls):
        try:
            async with cls._async_engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            logger.info("Database connection estabelished successfully.")
        except (OperationalError, ConnectionRefusedError):
            logger.exception("The connection was not successful")
            raise


class PostgresConnectionClient(DatabaseConnectionClient):
    @classmethod
    async def initialize(
        cls, connection_url: str, schema_name: str, debug: bool = False
    ):
        if "postgresql".casefold() not in connection_url.casefold():
            raise ValueError("The connection url must have a Postgres protocol")

        await cls._create_engine(connection_url, schema_name, debug)
        await cls._create_session()
        await cls._ping()
