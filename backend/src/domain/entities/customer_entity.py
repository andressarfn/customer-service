from pydantic import BaseModel


class CustomerInputEntity(BaseModel):
    name: str
    email: str


class CustomerOutputEntity(BaseModel):
    customer_id: int
    name: str | None = None
    email: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
