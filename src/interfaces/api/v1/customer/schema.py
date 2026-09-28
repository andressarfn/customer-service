from pydantic import BaseModel, EmailStr


class CustomerRequestSchema(BaseModel):
    name: str
    email: EmailStr


class CustomerResponseSchema(BaseModel):
    customer_id: int
    name: str | None = None
    email: EmailStr | None = None
    created_at: str | None = None
    updated_at: str | None = None
