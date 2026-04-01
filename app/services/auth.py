from app.schemas.user import UserCreate, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.security import hash_password, verify_password
from app.repositories import UserRepository 


class AuthService:
    def __init__(self, session : AsyncSession, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo

    # Регистрация пользователя в системе
    async def user_register(self, user_data: UserCreate) -> UserOut:

        # Проверка уникальности 
        existing = await self.user_repo.get_by_phone(user_data.phone)
        if existing: 
            raise ValueError("Пользователь с таким номером телефона уже существует")
        existing = await self.user_repo.get_by_username(user_data.username)
        if existing:
            raise ValueError("Имя пользователя занято")

        # Хеширование пароля пользователя
        hashed = hash_password(user_data.password)

        # Создаем пользователя с данными из запроса
        user = await self.user_repo.create_user(
            phone=user_data.phone,
            username=user_data.username,
            first_name=user_data.first_name,
            password_hash=hashed
        )
        
        # Коммит изменений
        await self.session.commit()
        # Возвращаем ответ, "прогоняя" его через Pydantic-схему
        return UserOut.model_validate(user)
    
    # Логин пользователя 
    async def user_authentication(self, phone: str, password: str) -> Optional[UserOut]:
        user = await self.user_repo.get_by_phone(phone)

        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        
        return UserOut.model_validate(user)
    
    