# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "TaskHub API"
    API_V1_STR: str = "/api/v1"

    # Lưu ý: Pydantic sẽ tự động tìm biến cùng tên trong file .env
    DATABASE_URL: str

    # Thiết lập để Pydantic đọc file .env
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Khởi tạo một object settings để import dùng ở mọi nơi
settings = Settings()
