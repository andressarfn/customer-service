from sqlalchemy import ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.models.base_model import Base


class FavoriteModel(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"))
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[str] = mapped_column(nullable=False, insert_default=func.now())
