from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from core.security import get_current_user
from schemas.chat import PrivateChatOut, GroupChatOut, ChatOut
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


