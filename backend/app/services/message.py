from sqlalchemy.ext.asyncio import AsyncSession
from repositories import MessageRepository, ChatRepository
from schemas import MessageOut
from typing import Optional, List
from core.security import encrypt_message
from datetime import datetime, timedelta, timezone

class MessageService:
    def __init__(self, session : AsyncSession, message_repo : MessageRepository, chat_repo : ChatRepository) -> None:
        self.session = session
        self.message_repo = message_repo
        self.chat_repo = chat_repo

    # Отправить сообщение
    async def send_message(self, sender_id : int, chat_id : int, text : str) -> MessageOut:

        if not await self.chat_repo.is_participant(chat_id, sender_id):
            raise PermissionError("Вы не являетесь участником чата")
        
        encrypted_content = encrypt_message(text)
        
        message = await self.message_repo.create(chat_id=chat_id,
                                                sender_id=sender_id,
                                                encrypted_content=encrypted_content)
        
        await self.session.commit()
        
        return MessageOut.model_validate(message)
    

    # Редактирование сообщений пользователя
    async def edit_message(self, user_id : int, message_id : int, new_text : str) -> Optional[MessageOut]:
        message = await self.message_repo.get_by_id(message_id)

        if not message:
            return None
        
        if message.sender_id != user_id: # type: ignore
            raise PermissionError("Нельзя редактировать чужие сообщения")
        
        #Если прошло больше 12 часов с момента отправки сообщения - выкидываем исключение
        if datetime.now(timezone.utc) - message.created_at > timedelta(hours=12): # type: ignore
            raise PermissionError("Нельзя редактировать сообщение, отправленное больше 12 часов назад")
        
        # Шифруем текст перед сохранением в БД
        encrypted_message = encrypt_message(new_text)
        
        updated_message = await self.message_repo.update(message_id, {"encrypted_text" : encrypted_message})

        if updated_message is None:
            return None 

        await self.session.commit()
        return MessageOut.model_validate(updated_message)


    # Удаление сообщения пользователя
    async def delete_message(self, user_id : int, message_id : int) -> bool: 
        
        message = await self.message_repo.get_by_id(message_id)

        if message is None:
            return False
        
        if datetime.now(timezone.utc) - message.created_at > timedelta(hours=12): #type: ignore
            raise PermissionError("Нельзя удалить сообщение, отправленное больше 12 часов назад")
        
        if message.sender_id != user_id: # type: ignore
            raise PermissionError("Нельзя удалять чужие сообщения")
        
        await self.message_repo.delete(message_id)
        await self.session.commit()

        return True
    
    
    # Отображение списка сообщений для пользователя
    async def get_chat_messages(self, user_id : int, chat_id : int, limit : int, offset : int) -> List[MessageOut]:
        
        if not await self.chat_repo.is_participant(chat_id, user_id):
            raise PermissionError("Вы не являетесь участником чата")
        
        messages = await self.message_repo.get_by_chat(chat_id=chat_id, 
                                                       limit=limit,
                                                       offset=offset)

        return [MessageOut.model_validate(msg) for msg in messages]



    








        


        
        

        

        


    

        
        