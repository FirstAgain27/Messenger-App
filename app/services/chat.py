from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import PrivateChatOut, GroupChatOut, ChatOut
from app.repositories import ChatRepository, UserRepository 
from typing import Optional, List
from app.models import GroupChat, ChatParticipant, Chat 
from sqlalchemy import select
from sqlalchemy.orm import selectin_polymorphic

class ChatService:
    def __init__(self, session: AsyncSession, chat_repo: ChatRepository, user_repo: UserRepository) -> None:
        self.session = session
        self.chat_repo = chat_repo
        self.user_repo = user_repo


    # Приватный метод для проверки группового чата
    async def _validate_group_chat(self, chat_id: int, user_id: int):
        chat = await self.chat_repo.get_by_id(chat_id)
        # Проверка существования чата 
        if chat is None:
            raise ValueError("Chat not found")
        # Проверка соответствия типа чата
        if not isinstance(chat, GroupChat):
            raise ValueError("Not a group chat")
        # Проверка соответствия id пользователя и id создателя чата
        if chat.creator_id != user_id: 
            raise PermissionError("Only creator can modify this group chat")
        return chat


    # Получение чатов пользователя
    async def get_user_chats(self, user_id: int) -> List[Chat]:
        stmt = (
            select(Chat)
            .options(selectin_polymorphic(Chat, [GroupChat]))
            .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
            .where(ChatParticipant.user_id == user_id)
            .where(ChatParticipant.deleted_by_user == False)
            .order_by(Chat.last_message_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    
    # Создание личного чата между пользователями
    async def create_private_chat(self, creator_id: int, other_user_id: int) -> Optional[PrivateChatOut]:

        other_user = await self.user_repo.get_by_id(other_user_id)
        if other_user is None:
            raise ValueError("User not found")
        
        if creator_id == other_user_id:
            raise ValueError("Cannot create chat with yourself")
        
        private_chat = await self.chat_repo.get_or_create_private(creator_id, other_user_id)
        await self.session.commit()

        return PrivateChatOut.model_validate({
            "id": private_chat.id,
            "other_user_id": other_user_id
        }) 


    # Создание группового чата 
    async def create_group_chat(self, creator_id: int, name: str, avatar: Optional[str], participant_ids: List[int]) -> GroupChatOut:

        """ Делаем id уникальными, выкидываем дубляжи и формируем список из приведенных к нужному формату id(Без повторений)"""
        unique_participants = set(participant_ids)
        # Явно добавляем создателя в список участников
        unique_participants.add(creator_id)
        normalized_ids = list(unique_participants)

        # Проверка переданных id
        existing_users = await self.user_repo.get_existing_ids(normalized_ids)
        if existing_users != set(normalized_ids):
            missing = set(normalized_ids) - existing_users
            raise ValueError(f"Пользователи с ID {missing} не существуют") 
        
        group_chat = await self.chat_repo.create_group_chat(creator_id=creator_id,
                                                            name=name,
                                                            avatar=avatar,
                                                            participants_ids=normalized_ids)

        await self.session.commit()

        # Создаем объект вручную, чтобы избежать ошибки с participants_ids
        return GroupChatOut(
            id=group_chat.id,
            type="group",
            name=group_chat.name,
            description=group_chat.description,
            avatar=group_chat.avatar,
            creator_id=group_chat.creator_id,
            participants_ids=normalized_ids,
            last_message_at=group_chat.last_message_at,
            created_at=group_chat.created_at
        )


    # Удаление чата только для одного пользователя (soft delete)
    async def hide_chat_for_user(self, user_id: int, chat_id: int) -> bool:
        result = await self.chat_repo.hide_chat_for_user(user_id=user_id, chat_id=chat_id) 
        if result:
            await self.session.commit()
        return result


    # Удаление группового чата создателем
    async def delete_the_group_by_creator(self, user_id: int, chat_id: int) -> bool:
        # Вызываем проверки
        await self._validate_group_chat(chat_id, user_id)
    
        deleted = await self.chat_repo.delete_chat(chat_id=chat_id)
        if deleted:
            await self.session.commit()
        return deleted
        
    
    # Частичное обновление группового чата
    async def update_group_chat(self, user_id: int, chat_id: int, updates: dict) -> Optional[GroupChatOut]:
        await self._validate_group_chat(chat_id, user_id)

        updated_chat = await self.chat_repo.update_group_chat(updates=updates, chat_id=chat_id)
        if not updated_chat:
            return None

        await self.session.commit()

        participants_ids = await self.chat_repo.get_participant_ids(chat_id)

        return GroupChatOut(
            id=updated_chat.id,
            type="group",
            name=updated_chat.name,
            description=updated_chat.description,
            avatar=updated_chat.avatar,
            creator_id=updated_chat.creator_id,
            participants_ids=participants_ids,
            last_message_at=updated_chat.last_message_at,
            created_at=updated_chat.created_at
        )
    


        





            
        
    


        




             
