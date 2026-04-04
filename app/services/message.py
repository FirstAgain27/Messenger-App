from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.message import MessageRepository
from app.repositories.chat import ChatRepository
from app.schemas.message import MessageOut
from app.core.security import encrypt_message
from app.core.websockets import manager # Наш синглтон-менеджер


class MessageService:
    def __init__(self, session: AsyncSession, message_repo: MessageRepository, chat_repo: ChatRepository) -> None:
        self.session = session
        self.message_repo = message_repo
        self.chat_repo = chat_repo

    async def _notify_participants(self, chat_id: int, sender_id: int, event_type: str, data: dict):
        """Вспомогательный метод для рассылки уведомлений всем участникам чата, кроме инициатора"""
        participants = await self.chat_repo.get_participant_ids(chat_id)
        notification = {
            "event": event_type,
            "chat_id": chat_id,
            **data
        }
        for user_id in participants:
            if user_id != sender_id:
                await manager.send_personal_message(user_id, notification)

    # Отправить сообщение
    async def send_message(self, sender_id: int, chat_id: int, text: str) -> MessageOut:
        chat = await self.chat_repo.get_by_id(chat_id)

        if not chat:
            raise ValueError("Chat not found")
        if not await self.chat_repo.is_participant(chat_id, sender_id):
            raise PermissionError("Вы не являетесь участником чата")
        
        encrypted_content = encrypt_message(text)
        
        message = await self.message_repo.create(
            chat_id=chat_id,
            sender_id=sender_id,
            encrypted_content=encrypted_content
        )
        
        await self.chat_repo.unhide_chat_for_all_participants(chat_id)
        await self.session.commit()
        await self.session.refresh(message)
        
        result = MessageOut(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            text=text,
            created_at=message.created_at
        )

        # Уведомляем остальных о новом сообщении
        await self._notify_participants(
            chat_id=chat_id, 
            sender_id=sender_id, 
            event_type="new_message",
            data={
                "message": result.model_dump(mode='json'),
                "text": text # Передаем расшифрованный текст для мгновенного отображения
            }
        )
        
        return result

    # Редактирование сообщений
    async def edit_message(self, user_id: int, message_id: int, new_text: str) -> Optional[MessageOut]:
        # 1. Получаем сообщение из базы
        message = await self.message_repo.get_by_id(message_id)

        # 2. Строгая проверка на None (убирает ошибку Pylance)
        if message is None:
            return None
        
        # 3. Проверки прав и времени
        if message.sender_id != user_id:
            raise PermissionError("Нельзя редактировать чужие сообщения")
        
        current_chat_id = message.chat_id 
        
        if datetime.now(timezone.utc) - message.created_at.replace(tzinfo=timezone.utc) > timedelta(hours=12):
            raise PermissionError("Нельзя редактировать сообщение старше 12 часов")
        
        # 4. Шифруем и обновляем
        encrypted_message = encrypt_message(new_text)
        updated_message = await self.message_repo.update(
            message_id, 
            {"encrypted_text": encrypted_message}
        )

        # 5. Еще одна проверка на случай, если update вернул None
        if updated_message is None:
            return None 

        await self.session.commit()
        await self.session.refresh(updated_message)
        
        result = MessageOut.model_validate(updated_message)

        # 6. Уведомление через WebSocket
        await self._notify_participants(
            chat_id=current_chat_id, # Используем сохраненный ID
            sender_id=user_id,
            event_type="edit_message",
            data={
                "message_id": message_id,
                "new_text": new_text
            }
        )

        return result

    # Удаление сообщения
    async def delete_message(self, user_id: int, message_id: int) -> bool: 
        message = await self.message_repo.get_by_id(message_id)

        # 1. Сначала строгая проверка на существование
        if not message:
            raise ValueError("Message not found")
        
        # Теперь Pylance знает, что здесь message — это точно объект Message, а не None
        if message.sender_id != user_id:
            raise PermissionError("Нельзя удалять чужие сообщения")
        
        # Сохраняем ID чата в переменную ДО удаления сообщения из базы
        chat_id = message.chat_id 
        
        await self.message_repo.delete(message_id)
        await self.session.commit()

        # Уведомляем участников
        await self._notify_participants(
            chat_id=chat_id,
            sender_id=user_id,
            event_type="delete_message",
            data={"message_id": message_id}
        )

        return True
    
    # Получение истории чата
    async def get_chat_history(self, user_id: int, chat_id: int, limit: int, offset: int) -> List[MessageOut]:
        if not await self.chat_repo.is_participant(chat_id, user_id):
            raise PermissionError("Вы не являетесь участником чата")
        
        messages = await self.message_repo.get_by_chat(chat_id=chat_id, limit=limit, offset=offset)
        return [MessageOut.model_validate(msg) for msg in messages]





        


        
        

        

        


    

        
        