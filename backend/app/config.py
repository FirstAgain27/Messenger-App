from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "FuckRKN"
    debug: bool = False
    secret_key: str  # Обязательно! Будет браться из .env
    
    # База данных
    database_url: str = "sqlite:///./messenger.db"
    
    # Безопасность
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite
        "http://localhost:3000",  # React
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Статика и файлы
    static_dir: str = "static"
    images_dir: str = "static/images"
    
    # JWT настройки (добавим позже)
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()