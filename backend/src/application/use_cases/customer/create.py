from dataclasses import dataclass

from loguru import logger

from src.domain.entities.customer_entity import (
    CustomerInputEntity,
    CustomerOutputEntity,
)
from src.domain.repositories.customer_repository_interface import (
    CustomerRepositoryInterface,
)


@dataclass(frozen=True)
class CreateCustomerUseCase:
    customer_repository: CustomerRepositoryInterface

    async def execute(
        self, customer_input_entity: CustomerInputEntity
    ) -> CustomerOutputEntity:
        logger.info("Creating a new customer")
        customer_id = await self.customer_repository.create(
            item=customer_input_entity,
        )

        logger.info(f"Customer created with ID: {customer_id}")
        return CustomerOutputEntity(customer_id=customer_id)
