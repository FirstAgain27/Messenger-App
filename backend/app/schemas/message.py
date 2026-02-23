from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional 
from datetime import datetime 

class MessageBase(BaseModel):
    text : str = Field(..., min_length=1, description="Текст сообщения")
    file_id : int | None = Field(None, description="ID прикрепленного файла")

class MessageCreate(MessageBase):
    pass


"""Определяет поля, которые будут возвращаться пользователю при любом запросе к серверу
по эндпоинту, связанному с Message
"""
class MessageOut(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

