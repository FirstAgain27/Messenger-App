from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


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
                                phone) -> User:

        user = User(username=username,
                    first_name=first_name,
                    password_hash=password_hash,
                    phone=phone)
        
        self.session.add(user)
        await self.session.flush()

        return user 
    

    # TODO: Добавить корутину для обновления пользователя
    async def update_user(self):
        pass
    
    """TODO: -Добавить обработку уникальности username
             -Добавить метод get_multi для получения списка пользователей с пагинацией
    """
    



         