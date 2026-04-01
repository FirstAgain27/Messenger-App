from schemas import UserCreate, UserUpdate, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from models import User

from core.security import hash_password, verify_password

from repositories import UserRepository 

class UserService:
    def __init__(self, session : AsyncSession, user_repo: UserRepository) -> None:
        self.session = session
        self.user_repo = user_repo
        
    # Обновление профиля пользователя
    async def user_profile_update(self, user_id : int, user_data : UserUpdate) -> Optional[UserOut]:
        # Берет в словарь только те поля, которые были переданы
        updates : dict = user_data.model_dump(exclude_unset=True)

        updated_user = await self.user_repo.update_user(user_id, updates)
        if not updated_user:
            return None

        await self.session.commit()

        return UserOut.model_validate(updated_user)
    
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
        
















        
            

    
