from app.schemas import UserCreate, UserUpdate, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models import User

from app.core.security import hash_password, verify_password

from app.repositories import UserRepository 

class UserService:
    def __init__(self, session : AsyncSession, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo
        
    # Обновление профиля пользователя
    async def user_profile_update(self, user_id: int, user_data: UserUpdate) -> User:
        # Если передан телефон, проверяем, не занят ли он другим пользователем
        if user_data.phone is not None:
            existing_user = await self.user_repo.get_by_phone(user_data.phone)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Phone already exists")

        # Остальная логика обновления
        updates = user_data.model_dump(exclude_unset=True)
        updated_user = await self.user_repo.update_user(user_id, updates)
        if updated_user is None:
            raise ValueError("User not found")
        await self.session.commit()
        return updated_user
    
    # Удаление профиля пользователя
    async def user_profile_delete(self, user_id: int, password: str) -> bool:
        # 1. Получаем пользователя через репозиторий
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # 2. Проверяем пароль
        if not verify_password(password, user.password_hash):
            return False
        
        # 3. Удаляем через репозиторий
        deleted = await self.user_repo.delete_user(user_id)
        
        # 4. Коммитим и возвращаем результат
        if deleted:
            await self.session.commit()
            return True
        
        return False
        
















        
            

    
