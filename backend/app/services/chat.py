from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PrivateChatOut, GroupChatOut
from repositories import ChatRepository, UserRepository 
from typing import Optional, List
from models import User 

class ChatService:
    def __init__(self, session : AsyncSession, chat_repo : ChatRepository, user_repo : UserRepository) -> None:
        self.session = session
        self.chat_repo = chat_repo
        self.user_repo = user_repo

    # Создание личного чата между пользователями
    async def create_private_chat(self, creator_id : int, other_user_id : int) -> Optional[PrivateChatOut]:

        other_user = await self.user_repo.get_by_id(other_user_id)
        if other_user is None:
            return None
        
        if creator_id == other_user_id:
            raise PermissionError("Нельзя создать чат с самим собой")
        
        private_chat = await self.chat_repo.get_or_create_private(creator_id, other_user_id)

        await self.session.commit()

        return PrivateChatOut.model_validate(private_chat, update = {"other_user_id" : other_user_id}) #type: ignore 


    # Создание группового чата 
    async def create_group_chat(self, creator_id : int, name : str, avatar : Optional[str], participant_ids : List[int]) -> GroupChatOut:

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

        return GroupChatOut.model_validate(group_chat, update={"participants_ids" : normalized_ids})


    # Удаление чата только для одного пользователя (soft delete)
    async def hide_chat_for_user(self, user_id: int, chat_id: int) -> bool:
        result = await self.chat_repo.hide_chat_for_user(user_id=user_id, chat_id=chat_id)

        if result:
            await self.session.commit()

        return result

    



    


            
        
    


        




             
