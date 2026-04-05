from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# === Входные схемы (Create) ===
class PrivateChatCreate(BaseModel):
    """Создание личного чата — клиент передаёт только ID второго участника."""
    other_user_id: int


class GroupChatCreate(BaseModel):
    """Создание группового чата — creator_id берётся из токена, поэтому в схеме его нет."""
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    participants_ids: list[int]   # ID участников (создатель добавится автоматически в сервисе)


# === Выходные схемы (Out) ===
class PrivateChatOut(BaseModel):
    """Ответ при создании/получении личного чата."""
    id: int
    other_user_id: int

    model_config = ConfigDict(from_attributes=True)


class GroupChatOut(BaseModel):
    """Ответ при создании/получении группового чата."""
    id: int
    type: str = "group"
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    creator_id: int
    participants_ids: list[int]
    last_message_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatOut(BaseModel):
    """Универсальная схема для списка чатов (и личных, и групповых)."""
    id: int
    type: str          # "private" или "group"
    name: Optional[str] = None      # для группы — название, для личного — имя собеседника (заполняется в сервисе)
    avatar: Optional[str] = None
    last_message_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# === Схема для обновления группового чата ===
class GroupChatUpdate(BaseModel):
    """Частичное обновление группового чата (только создателем)."""
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None