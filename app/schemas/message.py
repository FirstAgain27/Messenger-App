from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Входная схема (то, что присылает клиент)
class MessageCreate(BaseModel):
    chat_id: int = Field(..., description="ID чата, куда отправляем")
    text: str = Field(..., min_length=1, max_length=4096, description="Текст сообщения")

# Схема для обновления (PATCH)
class MessageUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)

# Выходная схема (то, что возвращает API)
class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

