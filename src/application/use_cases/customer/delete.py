from dataclasses import dataclass

from src.domain.repositories.customer_repository_interface import (
    CustomerRepositoryInterface,
)


@dataclass(frozen=True)
class DeleteCustomerUseCase:
    customer_repository: CustomerRepositoryInterface

    async def execute(self, customer_id: int) -> None:
        await self.customer_repository.delete(customer_id)
