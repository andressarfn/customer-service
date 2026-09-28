import traceback
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.customer_dto import CustomerInputDTO
from src.application.mappers.customer_mapper import CustomerMapper
from src.application.use_cases.customer.create import CreateCustomerUseCase
from src.application.use_cases.customer.delete import DeleteCustomerUseCase
from src.application.use_cases.customer.get import GetCustomerUseCase
from src.application.use_cases.customer.update import UpdateCustomerUseCase
from src.infrastructure.database.postgres_client import PostgresConnectionClient
from src.infrastructure.repositories.customer_repository import CustomerRepository
from src.infrastructure.repositories.exceptions import (
    EmailAlreadyExistsException,
    NotFoundException,
)
from src.interfaces.api.auth.dependencies import get_current_user
from src.interfaces.api.v1.customer.exceptions import (
    DeleteCustomerException,
    GetCustomerException,
    PostCustomerException,
    UpdateCustomerException,
)
from src.interfaces.api.v1.customer.schema import (
    CustomerRequestSchema,
    CustomerResponseSchema,
)

customer_v1_router = APIRouter(
    prefix="/v1", tags=["Customer"], dependencies=[Depends(get_current_user)]
)


@customer_v1_router.post(
    "/customer",
    description="Create a new customer",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomerResponseSchema,
    response_model_exclude_none=True,
)
async def create_customer(
    schema: Annotated[CustomerRequestSchema, Body(..., description="Create Customer")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
) -> CustomerResponseSchema:
    try:
        customer_input_dto = CustomerInputDTO(**schema.model_dump())
        customer_input_entity = CustomerMapper.to_entity(customer_input_dto)

        use_case = CreateCustomerUseCase(
            customer_repository=CustomerRepository(session),
        )
        customer_output_entity = await use_case.execute(customer_input_entity)
        return CustomerResponseSchema(**customer_output_entity.model_dump())
    except EmailAlreadyExistsException as e:
        raise e
    except Exception as e:
        raise PostCustomerException(
            title="Failed to create customer",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )


@customer_v1_router.get(
    "/customer/{customer_id}",
    description="Get a customer by ID",
    status_code=status.HTTP_200_OK,
    response_model=CustomerResponseSchema,
    response_model_exclude_none=True,
)
async def get_customer(
    customer_id: Annotated[int, Path(..., description="Customer ID")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
) -> CustomerResponseSchema:
    try:
        use_case = GetCustomerUseCase(
            customer_repository=CustomerRepository(session),
        )
        customer_output_entity = await use_case.execute(customer_id)
        return CustomerResponseSchema(**customer_output_entity.model_dump())
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise GetCustomerException(
            title="Failed to get customer",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )


@customer_v1_router.patch(
    "/customer/{customer_id}",
    description="Update a customer by ID",
    status_code=status.HTTP_200_OK,
    response_model=CustomerResponseSchema,
)
async def update_customer(
    customer_id: Annotated[int, Path(..., description="Customer ID")],
    schema: Annotated[CustomerRequestSchema, Body(..., description="Update Customer")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
) -> CustomerResponseSchema:
    try:
        customer_input_dto = CustomerInputDTO(**schema.model_dump())
        customer_input_entity = CustomerMapper.to_entity(customer_input_dto)

        use_case = UpdateCustomerUseCase(
            customer_repository=CustomerRepository(session),
        )
        customer_output_entity = await use_case.execute(
            customer_id, customer_input_entity
        )
        return CustomerResponseSchema(**customer_output_entity.model_dump())
    except (NotFoundException, EmailAlreadyExistsException) as e:
        raise e
    except Exception as e:
        raise UpdateCustomerException(
            title="Failed to update customer",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )


@customer_v1_router.delete(
    "/customer/{customer_id}",
    description="Delete a customer by ID",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_customer(
    customer_id: Annotated[int, Path(..., description="Customer ID")],
    session: Annotated[AsyncSession, Depends(PostgresConnectionClient.session)],
) -> None:
    try:
        use_case = DeleteCustomerUseCase(
            customer_repository=CustomerRepository(session),
        )
        await use_case.execute(customer_id)
    except NotFoundException as e:
        raise e
    except Exception as e:
        raise DeleteCustomerException(
            title="Failed to delete customer",
            detail={"exception": e.__class__.__name__, "message": str(e)},
            traceback=traceback.format_exc(),
        )
