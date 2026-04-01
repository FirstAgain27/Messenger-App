from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Схема для ВХОДА (что присылает юзер)
class MessageCreate(BaseModel):
    chat_id: int = Field(..., description="ID чата, куда отправляем")
    text: str = Field(..., min_length=1, max_length=4096, description="Текст сообщения")
    file_id: Optional[int] = Field(None, description="ID файла, если есть")

# Схема для ОБНОВЛЕНИЯ (PATCH)
class MessageUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)

# Схема для ВЫХОДА (что отдает API)
class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    file_id: Optional[int]
    created_at: datetime
    # Поля, которых нет на входе, но есть в БД
    is_edited: bool = False
    
    model_config = ConfigDict(from_attributes=True)

