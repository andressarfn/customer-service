from dataclasses import dataclass

from src.domain.entities.customer_entity import (
    CustomerInputEntity,
    CustomerOutputEntity,
)
from src.domain.repositories.customer_repository_interface import (
    CustomerRepositoryInterface,
)


@dataclass(frozen=True)
class UpdateCustomerUseCase:
    customer_repository: CustomerRepositoryInterface

    async def execute(
        self, customer_id: int, customer_input_entity: CustomerInputEntity
    ) -> CustomerOutputEntity:
        customer_entity = await self.customer_repository.update(
            customer_id, customer_input_entity
        )
        return CustomerOutputEntity(
            customer_id=customer_entity.id,
            name=customer_entity.name,
            email=customer_entity.email,
            created_at=str(customer_entity.created_at),
            updated_at=str(customer_entity.updated_at),
        )
