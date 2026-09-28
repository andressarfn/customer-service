from dataclasses import dataclass

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.customer_repository_interface import (
    CustomerRepositoryInterface,
)
from src.infrastructure.models.customer_model import CustomerModel
from src.infrastructure.repositories.exceptions import (
    EmailAlreadyExistsException,
    NotFoundException,
)


@dataclass(frozen=True)
class CustomerRepository(CustomerRepositoryInterface):
    session: AsyncSession
    model: type = CustomerModel

    async def create(self, item: BaseModel) -> int:
        try:
            stmt = (
                insert(self.model).values(**item.model_dump()).returning(self.model.id)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                logger.error("Email already exists in the database")
                raise EmailAlreadyExistsException(
                    title="Email already exists",
                    detail="A customer with this email address already exists.",
                    status_code=400,
                )

    async def get_by_id(self, id: int) -> BaseModel | None:
        stmt = select(self.model).where(self.model.id == id).limit(1)
        get = await self.session.execute(stmt)
        result = get.scalar_one_or_none()
        if result is None:
            logger.error(f"Customer with id {id} not found")
            raise NotFoundException(
                title="customer_id not found",
                detail=f"No customer found with id {id}",
                status_code=400,
            )
        logger.info(f"Customer with id {id} retrieved successfully")
        return result

    async def update(self, id: int, item: BaseModel) -> BaseModel | None:
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**item.model_dump(exclude={"created_at"}))
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            customer = result.scalar_one_or_none()
            if customer is None:
                logger.error(f"Customer with id {id} not found for update")
                raise NotFoundException(
                    title="customer_id not found",
                    detail=f"No customer found with id {id}",
                    status_code=400,
                )
            logger.info(f"Customer with id {id} updated successfully")
            return customer
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                logger.error("Email already exists in the database")
                raise EmailAlreadyExistsException(
                    title="Email already exists",
                    detail="A customer with this email address already exists.",
                    status_code=400,
                )

    async def delete(self, id: int) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        deleted = bool((await self.session.execute(stmt)).rowcount)
        if not deleted:
            logger.error(f"Customer with id {id} not found for deletion")
            raise NotFoundException(
                title="customer_id not found",
                detail=f"No customer found with id {id}",
                status_code=400,
            )
        logger.info(f"Customer with id {id} deleted successfully")
