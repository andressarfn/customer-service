from src.infrastructure.external_services.client import Client
from src.infrastructure.external_services.products.product_client import ProductClient


def get_product_client() -> ProductClient:
    return ProductClient(Client())
