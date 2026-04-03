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

@pytest.mark.asyncio
async def test_login_success(setup_db, ac: AsyncClient):
    # 1. Регистрируем пользователя
    user_data = {
        "phone": "+79657357259123",
        "username": "logintest",
        "first_name": "Login",
        "password": "testpass123"
    }
    register_response = await ac.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201

    # 2. Логинимся
    login_data = {
        "phone": user_data["phone"],
        "password": user_data["password"]
    }
    response = await ac.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(setup_db, ac: AsyncClient):
    # Регистрируем
    user_data = {
        "phone": "+79657357259124",
        "username": "wrongpasstest",
        "first_name": "Wrong",
        "password": "correctpass"
    }
    await ac.post("/api/auth/register", json=user_data)

    # Логинимся с неверным паролем
    login_data = {
        "phone": user_data["phone"],
        "password": "wrongpass"
    }
    response = await ac.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_duplicate_phone(setup_db, ac: AsyncClient):
    """Попытка регистрации с уже существующим телефоном"""
    user_data = {
        "phone": "+79657357259123",
        "username": "user1",
        "first_name": "User",
        "password": "pass1234"
    }
    await ac.post("/api/auth/register", json=user_data)
    response = await ac.post("/api/auth/register", json=user_data)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_register_invalid_phone(setup_db, ac: AsyncClient):
    """Телефон неправильной длины (Pydantic валидация)"""
    user_data = {
        "phone": "+123",  # слишком короткий
        "username": "user2",
        "first_name": "User",
        "password": "pass"
    }
    response = await ac.post("/api/auth/register", json=user_data)
    assert response.status_code == 422 

@pytest.mark.asyncio
async def test_login_nonexistent_phone(setup_db, ac: AsyncClient):
    """Логин с несуществующим телефоном"""
    login_data = {
        "phone": "+79657357259999",
        "password": "anypass88"
    }
    response = await ac.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

    