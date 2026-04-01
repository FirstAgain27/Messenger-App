from sqlalchemy.ext.asyncio import AsyncSession
from schemas.chat import PrivateChatOut, GroupChatOut, ChatOut
from repositories import ChatRepository, UserRepository 
from typing import Optional, List
from models import GroupChat

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
    async def get_user_chats(self, user_id: int) -> List[ChatOut]:
        current_user = await self.user_repo.get_by_id(user_id)
        if not current_user:
            raise ValueError("User not found")
        
        chats = await self.chat_repo.get_user_chats(user_id=user_id)
        
        # Возвращаем Pydantic-схемы
        return [ChatOut.model_validate(chat) for chat in chats]
        
    
    # Создание личного чата между пользователями
    async def create_private_chat(self, creator_id: int, other_user_id: int) -> Optional[PrivateChatOut]:

        other_user = await self.user_repo.get_by_id(other_user_id)
        if other_user is None:
            raise ValueError("User not found")
        
        if creator_id == other_user_id:
            raise ValueError("Cannot create chat with yourself")
        
        private_chat = await self.chat_repo.get_or_create_private(creator_id, other_user_id)
        await self.session.commit()

        return PrivateChatOut.model_validate(private_chat, update = {"other_user_id" : other_user_id}) #type: ignore 


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

        chat_dto = GroupChatOut.model_validate(group_chat)
        # Возвращаем Data Transfer Object с полем participants_ids
        return chat_dto.model_copy(update={"participants_ids" : normalized_ids})


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
        # Проверяем права (существует ли чат и является ли пользователь участником/админом)
        await self._validate_group_chat(chat_id, user_id)

        # Обновляем данные в репозитории
        updated_chat = await self.chat_repo.update_group_chat(updates=updates, chat_id=chat_id)
        if not updated_chat:
            return None
        
        # Сохраняем транзакцию
        await self.session.commit()

        return GroupChatOut.model_validate(updated_chat)
    


        





            
        
    


        




             
