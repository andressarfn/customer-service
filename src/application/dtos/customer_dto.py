from pydantic import BaseModel


class CustomerInputDTO(BaseModel):
    name: str
    email: str
