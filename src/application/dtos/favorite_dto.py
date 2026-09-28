from pydantic import BaseModel


class FavoriteInputDTO(BaseModel):
    customer_id: int
    product_id: int
