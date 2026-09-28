from pydantic import BaseModel


class FavoriteRequestSchema(BaseModel):
    product_id: int


class ProductFavoriteSchema(BaseModel):
    price: float
    image: str
    brand: str
    id: int
    title: str
    reviewScore: float


class FavoritesResponseSchema(BaseModel):
    customer_id: int
    favorites: list[ProductFavoriteSchema]


class FavoriteResponseSchema(BaseModel):
    message: str = "Favorite item added successfully"
