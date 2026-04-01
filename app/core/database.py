from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Подготовка URL для асинхронного драйвера
if settings.database_url.startswith("sqlite"):
    # Заменяем sqlite:// на sqlite+aiosqlite://
    db_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    db_url = settings.database_url

# Создаём асинхронный движок
engine = create_async_engine(
    db_url,
    echo=settings.debug,
    # Для SQLite нужно отключить проверку потоков
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Создаём фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """Асинхронная зависимость для получения сессии БД."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Создание таблиц (для разработки)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрытие соединения с БД."""
    await engine.dispose()
    