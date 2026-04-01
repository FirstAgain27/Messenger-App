import os
import pytest
from httpx import AsyncClient, ASGITransport

# Тестовые переменные
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["encryption_key"] = "75S-s7-A6_p93_3y123456789012345678901234567="

from app.main import app
from app.core.database import engine, Base

@pytest.fixture
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)