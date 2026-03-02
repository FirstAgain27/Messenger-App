from typing import Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


from app.models import User

"""Repositories - используются для создания методов получения данных из БД.
 B дальнейшем используются в бизнес-логике для улучшения читаемости"""

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Получение пользователя по user_id
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)
    
    # Получение пользователя по номеру телефона
    async def get_by_phone(self, phone: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()
    
    # Получение пользователя по username
    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.username==username))
        return result.scalar_one_or_none()
        
    # Создание пользователя
    async def create_user(self, username: str,
                                first_name: str,
                                password_hash: str,
                                phone: str) -> User:

        user = User(username=username,
                    first_name=first_name,
                    password_hash=password_hash,
                    phone=phone)
        
        self.session.add(user)
        await self.session.flush()

        return user 
    
    # Редактирование пользователя
    async def update_user(self, user_id : int, updates : dict) -> Optional[User]:
        
        user = await self.session.get(User, user_id)

        if user is None:
            return None
        
        allowed_fields : Set[str] = {"phone", "username", "first_name", 
                                     "last_name", "email", "bio", "avatar_url"}
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None: 
                setattr(user, field, value)
            
        await self.session.flush()
    
        return user
    
    # Удаление пользователя
    async def delete_user(self, user_id : int) -> bool:
        user = await self.session.get(User, user_id)

        if user is None:
            return False
        
        await self.session.delete(user)
        await self.session.flush()

        return True

  
    






        
        
        
        
        
        
    



         