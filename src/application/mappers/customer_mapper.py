from src.application.dtos.customer_dto import CustomerInputDTO
from src.domain.entities.customer_entity import CustomerInputEntity


class CustomerMapper:
    @staticmethod
    def to_entity(dto: CustomerInputDTO) -> CustomerInputEntity:
        return CustomerInputEntity(**dto.model_dump())
