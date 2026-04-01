import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_user_register(setup_db, ac: AsyncClient):
    user_data = {
        "first_name": "OchenKrutoeImya",
        "password": "1298ajfasi3189jn",
        "phone": "+79657357259",
        "username": "testuser"
    }


    response = await ac.post("/api/auth/register", json=user_data)
    print(response.json())

    assert response.status_code == 201

    data = response.json()

    # Проверяем, что передались корректные данные
    assert data["username"] == user_data["username"]
    assert data["phone"] == user_data["phone"]
    
    # Проверяем, что база присвоила ID  
    assert "id" in data
    # Если в data придет поле password — тест упадет    
    assert "password" not in data
