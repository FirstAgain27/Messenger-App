from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Базовые поля пользователя"""
    phone: str = Field(..., description="Номер телефона (с '+' или без)")
    username: str = Field(..., min_length=3, max_length=33, description="Уникальное имя пользователя")
    first_name: str = Field(..., min_length=1, max_length=64, description="Имя")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валидация телефонного номера: допускает + и цифры, длина от 10 до 15"""
        cleaned = re.sub(r'\D', '', v)  # удаляем всё кроме цифр
        if not 10 <= len(cleaned) <= 15:
            raise ValueError('Номер телефона должен содержать от 10 до 15 цифр')
        # Приводим к единому формату: если нет + в начале, добавляем
        if not v.startswith('+'):
            v = '+' + cleaned
        return v


class UserCreate(UserBase):
    """Создание пользователя"""
    password: str = Field(..., min_length=8, max_length=128, description="Пароль")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Базовая проверка сложности пароля"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        return v


class UserOut(UserBase):
    """Выходные данные пользователя (без пароля)"""
    id: int
    email: Optional[EmailStr] = None
    last_name: Optional[str] = Field(None, max_length=64)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    created_at: datetime
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Обновление профиля (все поля опциональны)"""
    phone: Optional[str] = Field(None, description="Номер телефона")
    username: Optional[str] = Field(None, min_length=3, max_length=33)
    first_name: Optional[str] = Field(None, min_length=1, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r'\D', '', v)
        if not 10 <= len(cleaned) <= 15:
            raise ValueError('Номер телефона должен содержать от 10 до 15 цифр')
        if not v.startswith('+'):
            v = '+' + cleaned
        return v


class UserDeleteRequest(BaseModel):
    """Подтверждение удаления аккаунта"""
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Неверный пароль')
        return v