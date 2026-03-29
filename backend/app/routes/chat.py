from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from core.security import get_current_user
from schemas.chat import (PrivateChatOut, 
                          GroupChatOut, 
                          ChatOut, 
                          GroupChatCreate, 
                          PrivateChatCreate, 
                          GroupChatUpdate)
from repositories.chat import ChatRepository
from repositories.user import UserRepository
from services.chat import ChatService
from models import User, Chat


router = APIRouter(prefix='/api/chats', tags=["chats"])

# Список чатов пользователя
@router.get("/", response_model=List[ChatOut])
async def get_chats(
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
    ):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(db, chat_repo, user_repo)

    try:
        chats = await chat_service.get_user_chats(user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    return chats

# Создание группового чата
@router.post("/group", response_model=GroupChatOut, status_code=status.HTTP_201_CREATED)
async def create_group_chat(
    chat_data : GroupChatCreate,
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
    ):
    chat_repo = ChatRepository(db)
    user_repo = UserRepository(db)
    chat_service = ChatService(db, chat_repo, user_repo)

    try:
        group_chat = await chat_service.create_group_chat(creator_id=current_user.id,
                                             name=chat_data.name,
                                             avatar=chat_data.avatar,
                                             participant_ids=chat_data.participants_ids
                                             )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

    return group_chat

# Создание личного чата
@router.post("/private", response_model=PrivateChatOut, status_code=status.HTTP_201_CREATED)
async def create_private_chat(
    chat_data : PrivateChatCreate,
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
    ):
    chat_repo = ChatRepository(db)
    user_repo = UserRepository(db)
    chat_service = ChatService(db, chat_repo, user_repo)

    try:
        private_chat = await chat_service.create_private_chat(
            creator_id=current_user.id,
            other_user_id=chat_data.other_user_id
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

    return private_chat


# Мягкое удаление чата пользователем 
@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id : int,
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
    ):
    chat_repo = ChatRepository(db)
    user_repo = UserRepository(db)
    chat_service = ChatService(db, chat_repo, user_repo)

    success = await chat_service.hide_chat_for_user(user_id=current_user.id,
                                                    chat_id=chat_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or you are not a participant"
        )
    
    return None


# Удаление группового чата
@router.delete("/group/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_chat(
    chat_id : int,
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
    ):

    chat_repo = ChatRepository(db)
    user_repo = UserRepository(db)
    chat_service = ChatService(db, chat_repo, user_repo)

    success = await chat_service.delete_the_group_by_creator(user_id=current_user.id,
                                                    chat_id=chat_id)
    
    try:
        success = await chat_service.delete_the_group_by_creator(
            user_id=current_user.id,
            chat_id=chat_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")

    return None

@router.patch("/{chat_id}", response_model=GroupChatOut)
async def update_group_chat(
    chat_id: int,
    # Используем схему вместо dict
    update_data: GroupChatUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ): 
    # Включаем только те поля, которые пользователь реально прислал
    updates = update_data.model_dump(exclude_unset=True)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    chat_service = ChatService(db, ChatRepository(db), UserRepository(db))

    try:
        updated = await chat_service.update_group_chat(
            user_id=current_user.id,
            chat_id=chat_id,
            updates=updates
        )
    except ValueError as e:
        # Если чат не найден — 404, если данные плохие — 400
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    return updated