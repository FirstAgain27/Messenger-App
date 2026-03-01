from typing import Optional, Set, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models import Message

class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    # Сохранить зашифрованное сообщение в БД
    async def create(self, chat_id : int, 
                           sender_id : int, 
                           encrypted_content : bytes,
                           iv : bytes) -> Message:
        
        message = Message(chat_id=chat_id,
                          sender_id=sender_id,
                          encrypted_content=encrypted_content,
                          iv=iv)
        
        self.session.add(message)
        await self.session.flush()
        return message


    # Удаление сообщения из бд
    async def delete(self, id: int) -> bool:
        
        message = await self.session.scalar(select(Message).where(Message.id == id))

        if message is None:
            return False
        
        await self.session.delete(message)
        await self.session.flush()

        return True 
    

    # Редактирование сообщения 
    async def update(self, id: int, updates : dict[str, bytes]) -> Message | None:
        message = await self.session.scalar(select(Message).where(Message.id == id))

        if message is not None:
            allowed_fields : Set[str] = {"encrypted_text"}
            for field, value in updates.items():
                if field in allowed_fields and value is not None: 
                    setattr(message, field, value)
        
            await self.session.flush()

        return message


    # Получение сообщения по id 
    async def get_by_id(self, id : int) -> Optional[Message]:
        result = await self.session.get(Message, id)

        return result


    # Получение всех сообщений из конкретного чата
    async def get_by_chat(self, chat_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
    
        result = await self.session.execute(select(Message)
                                            .where(Message.chat_id == chat_id)
                                            .order_by(Message.created_at.desc())
                                            .offset(offset)
                                            .limit(limit)
                                            )
        
        return result.scalars().all() # type: ignore
    

