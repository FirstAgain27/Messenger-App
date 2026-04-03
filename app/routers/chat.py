from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.chat import (PrivateChatOut, 
                          GroupChatOut, 
                          ChatOut, 
                          GroupChatCreate, 
                          PrivateChatCreate, 
                          GroupChatUpdate)
from app.repositories.chat import ChatRepository
from app.repositories.user import UserRepository
from app.services.chat import ChatService
from app.models import User

router = APIRouter(prefix='/api/chats', tags=["chats"])

# Вспомогательная зависимость для инициализации сервиса
async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db, ChatRepository(db), UserRepository(db))

# Список чатов пользователя
@router.get("/", response_model=List[ChatOut])
async def get_chats(
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return await service.get_user_chats(user_id=current_user.id)

# Создание группового чата
@router.post("/group", response_model=GroupChatOut, status_code=status.HTTP_201_CREATED)
async def create_group_chat(
    chat_data: GroupChatCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    try:
        return await service.create_group_chat(
            creator_id=current_user.id,
            name=chat_data.name,
            avatar=chat_data.avatar,
            participant_ids=chat_data.participants_ids
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Создание личного чата
@router.post("/private", response_model=PrivateChatOut, status_code=status.HTTP_201_CREATED)
async def create_private_chat(
    chat_data: PrivateChatCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    try:
        return await service.create_private_chat(
            creator_id=current_user.id,
            other_user_id=chat_data.other_user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Мягкое удаление чата пользователем (скрыть из списка)
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    success = await service.hide_chat_for_user(user_id=current_user.id, chat_id=chat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chat not found or you are not a participant"
        )
    return None

# Полное удаление группового чата (только создателем)
@router.delete("/group/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    try:
        success = await service.delete_the_group_by_creator(
            user_id=current_user.id,
            chat_id=chat_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return None

# Частичное обновление группового чата (только создателем)
@router.patch("/{chat_id}", response_model=GroupChatOut)
async def update_group_chat(
    chat_id: int,
    update_data: GroupChatUpdate, 
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
): 
    updates = update_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    try:
        return await service.update_group_chat(
            user_id=current_user.id,
            chat_id=chat_id,
            updates=updates
        )
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))