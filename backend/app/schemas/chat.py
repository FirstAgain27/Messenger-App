from pydantic import BaseModel, Field, EmailStr, ConfigDict, List
from typing import Optional 
from datetime import datetime 


class ChatBase(BaseModel):
    id : int
    type : str
    last_message_at : Optional[datetime]
    created_at : datetime


# Содержит данные, которые получаем от клиента, больше никакие другие(То, что заполняется автоматически - не пишем)
class PrivateChatCreate(BaseModel):
    other_user_id : int # ID второго участника

# Содержит данные, которые получаем от клиента, больше никакие другие(То, что заполняется автоматически - не пишем)
class GroupChatCreate(BaseModel):
    name : str 
    creator_id : int
    description : Optional[str] = None
    avatar : Optional[str] = None 
    participants_ids : List[int] # ID участников


class PrivateChatOut(ChatBase):
    other_user_id : int 


class GroupChatOut(ChatBase):
    name : str 
    description : Optional[str]
    avatar : Optional[str]
    creator_id : int
    participants_ids : List[int] 


# Схема для обоих типов чатов
class ChatOut(BaseModel):
    id : int 
    type : str
    name : str | None = None
    avatar : str | None = None
    last_message_at : datetime




    




