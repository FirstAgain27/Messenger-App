from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user, get_current_user_ws
from core.websockets import manager 
from models import User

from services.message import MessageService
from schemas import MessageOut, MessageCreate
from repositories import ChatRepository, MessageRepository

router = APIRouter(prefix='/api/messages', tags=['messages'])

# Зависимость для получения сервиса
async def get_message_service(db: AsyncSession = Depends(get_db)):
    return MessageService(db, MessageRepository(db), ChatRepository(db))

# Подключение websocket
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token_user_id: int = Depends(get_current_user_ws)
):
    # Проверяем соответствие user_id в токене с полученным user_id
    if token_user_id != user_id:
        await websocket.close(code=1008)
        return 
    
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Заготовка на будущее, чтобы сохранять то, что прислал клиент
            data = await websocket.receive_text()

    # Срабатывает, когда клиент сам разорвал связь 
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    # Страховка на случай других непредвиденных ошибок
    except Exception:
        manager.disconnect(user_id, websocket)

# Отправка сообщения
@router.post("/", response_model=MessageOut)
async def send_message(
    data = MessageCreate,
    service: MessageService = Depends(get_message_service),
    current_user : User = Depends(get_current_user),
    ):

    try:
        return await service.send_message(
            sender_id=current_user.id,
            chat_id=data.chat_id,
            text=data.text
            )

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Получить историю сообщений чата
@router.get("/{chat_id}", response_model=MessageOut)
async def get_message_history(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
    ):
    
    try:
        return await service.get_chat_history(user_id=current_user.id,
                                              chat_id=chat_id,
                                              limit=limit,
                                              offset=offset)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
# Удалить сообщение (для всех)
@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
    ):  

    try:
        return await service.delete_message(user_id=current_user.id,
                                            message_id=message_id)
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return None

