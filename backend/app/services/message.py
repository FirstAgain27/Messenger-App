from sqlalchemy.ext.asyncio import AsyncSession
from repositories import MessageRepository, ChatRepository
from schemas import MessageCreate, MessageOut
from typing import Optional
from core.security import encrypt_message


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
    
        

        

        


    

        
        