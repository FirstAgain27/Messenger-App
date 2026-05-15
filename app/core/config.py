from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "FuckRKN"
    debug: bool = False
    SECRET_KEY : str

    # База данных
    database_url: str = "sqlite:///./messenger.db"

    # Безопасность: ключ для Fernet (32 байта в urlsafe base64)
    encryption_key: str

    # CORS
    cors_origins: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    ]

    # Статика
    static_dir: str = "static"
    images_dir: str = "static/images"

    # JWT 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()