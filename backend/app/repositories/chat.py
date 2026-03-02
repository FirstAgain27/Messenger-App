from typing import Optional, Set, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_

from app.models import Chat, GroupChat, ChatParticipant

class ChatRepository:
    def __init__(self, session : AsyncSession) -> None:
        self.session = session 

    # Получение чата по id 
    async def get_by_id(self, chat_id : int) -> Optional[Chat]:
        return await self.session.get(Chat, chat_id)

    # Получение всех чатов пользователя
    async def get_user_chats(self, user_id : int) -> List[Chat]:
        result = await self.session.execute(select(Chat).
                                            join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
                                            .where(ChatParticipant.user_id == user_id)
                                            .order_by(Chat.last_message_at.desc())
                                            )
        
        return result.scalars().all()
    

    # Поиск чата и его создание в случае отсутствия
    async def get_or_create_private(self, user1_id: int, user2_id: int) -> Chat:

        chat = await self.session.execute(select(Chat)
                                        .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
                                        .where(Chat.type == "chat")
                                        .group_by(Chat.id)
                                        .having(and_(func.count(ChatParticipant.user_id) == 2,
                                                    func.sum(case((ChatParticipant.user_id == user1_id, 1), else_=0)) == 1,
                                                    func.sum(case((ChatParticipant.user_id == user2_id, 1), else_=0)) == 1
                                                    )))
        
        chat = chat.scalar_one_or_none()
            
        if chat is not None:
            return chat

        new_chat = Chat(type='chat')
        self.session.add(new_chat)

        await self.session.flush()

        participant1 = ChatParticipant(chat_id=new_chat.id, user_id=user1_id)
        participant2 = ChatParticipant(chat_id=new_chat.id, user_id=user2_id)
        self.session.add_all([participant1, participant2])
        await self.session.flush()

        return new_chat

    async def delete_chat(self, chat_id : int) -> bool:
        chat = await self.session.get(Chat, chat_id)

        if chat is not None:
            await self.session.delete(chat)
            await self.session.flush()
            return True
        
        return False
    
    async def update_group_chat(self, updates : dict, chat_id: int) -> Optional[GroupChat]:

        chat = await self.session.scalar(select(Chat).where(Chat.id == chat_id, Chat.type == "group"))

        if chat is None:
            return None
        
        allowed_fields = {"name", "description", "avatar"}

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(chat, field, value)
        
        await self.session.flush()
        return chat
        







        




    
    
    

        

    