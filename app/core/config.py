import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TaskHub API"
    API_V1_STR: str = "/api/v1"

    # --- Project Settings ---
    ENVIRONMENT: Literal["dev", "test", "prod"] = "dev"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["*"], description="Danh sách các domain được phép gọi API (CORS)"
    )

    # --- Database Settings ---
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")

    # --- Auth Settings ---
    SECRET_KEY: str = Field(
        ..., min_length=32, description="Secret key phải dài ít nhất 32 ký tự"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, gt=0, description="Thời gian sống của Token phải lớn hơn 0"
    )

    # --- Redis Settings ---
    REDIS_HOST: str = Field(default="localhost", min_length=1)
    REDIS_PORT: int = Field(
        default=6379, ge=1, le=65535, description="Port hợp lệ từ 1 đến 65535"
    )
    REDIS_DB: int = Field(default=0, ge=0)
    REDIS_PASSWORD: str | None = None

    # Thiết lập để Pydantic đọc file .env
    # Mẹo: Đọc file .env gốc trước (chứa các biến mặc định),
    # sau đó đọc file .env.{môi_trường} để ghi đè (override).
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('ENVIRONMENT', 'dev')}"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Khởi tạo một object settings để import dùng ở mọi nơi
settings = Settings()  # type: ignore
