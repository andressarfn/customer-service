import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Customer Service"
    DESCRIPTION: str = "Study Project"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SERIALIZE_LOGS: bool = True
    LOG_LEVEL: str = "INFO"

    ROOT_PATH: str = "customer-service"

    DATABASE_URL: str = ""
    DATABASE_SCHEMA: str = ""

    PRODUCT_CLIENT_URL: str = (
        "https://a38cdba7-87da-46a5-ada1-eb72692ddb34.mock.pstmn.io"
    )

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60

    class Config:
        env_file = "ENV_FILE" if "ENV_FILE" in os.environ else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
