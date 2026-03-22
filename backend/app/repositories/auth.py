from typing import Optional, Set, List 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


from app.models import User

class AuthRepository:
    def __init__(self, session : AsyncSession) -> None:
        self.session = session

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
