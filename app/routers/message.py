from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user, get_current_user_ws
from app.core.websockets import manager
from app.models import User
from app.services.message import MessageService
from app.schemas import MessageOut, MessageCreate
from app.repositories import ChatRepository, MessageRepository

router = APIRouter(prefix='/api/messages', tags=['messages'])

# --- Зависимости для HTTP ---
async def get_message_service(db: AsyncSession = Depends(get_db)):
    return MessageService(db, MessageRepository(db), ChatRepository(db))

async def get_chat_repo(db: AsyncSession = Depends(get_db)):
    return ChatRepository(db)

# --- WebSocket ---
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token_user_id: Optional[int] = Depends(get_current_user_ws)
):
    # Если токен невалиден или не совпадает user_id, сокет уже закрыт, просто выходим
    if token_user_id is None or token_user_id != user_id:
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Принимаем JSON с сообщением
            data = await websocket.receive_json()
            if data.get("type") != "message":
                continue
            chat_id = data.get("chat_id")
            text = data.get("text")
            if not chat_id or not text:
                continue

            # Создаём отдельную сессию БД для операции
            async with AsyncSessionLocal() as db:
                service = MessageService(db, MessageRepository(db), ChatRepository(db))
                chat_repo = ChatRepository(db)
                try:
                    # Сохраняем сообщение
                    message = await service.send_message(
                        sender_id=user_id,
                        chat_id=chat_id,
                        text=text
                    )
                    # Получаем участников чата
                    participants = await chat_repo.get_participant_ids(chat_id)
                    # Рассылаем всем участникам (включая отправителя, чтобы обновить UI)
                    await manager.broadcast_to_chat(
                        chat_id=chat_id,
                        message={"type": "new_message", "message": message.model_dump()},
                        participant_ids=participants,
                        exclude_user_id=None  # можно исключить отправителя, но лучше отправить всем
                    )
                except (PermissionError, ValueError) as e:
                    # Отправляем ошибку обратно в сокет
                    await websocket.send_json({"type": "error", "detail": str(e)})
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)

# --- HTTP эндпоинты ---
@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    service: MessageService = Depends(get_message_service),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    current_user: User = Depends(get_current_user),
):
    try:
        message = await service.send_message(
            sender_id=current_user.id,
            chat_id=data.chat_id,
            text=data.text
        )
        # Рассылка через WebSocket
        participants = await chat_repo.get_participant_ids(data.chat_id)
        await manager.broadcast_to_chat(
            chat_id=data.chat_id,
            message={"type": "new_message", "message": message.model_dump()},
            participant_ids=participants,
            exclude_user_id=current_user.id
        )
        return message
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{chat_id}", response_model=List[MessageOut])
async def get_message_history(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    try:
        return await service.get_chat_history(
            user_id=current_user.id,
            chat_id=chat_id,
            limit=limit,
            offset=offset
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    try:
        await service.delete_message(
            user_id=current_user.id,
            message_id=message_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    