from pydantic import BaseModel, Field, ConfigDict
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
    model_config = ConfigDict(from_attributes=True )

    name : str 
    creator_id : int
    description : Optional[str] = None
    avatar : Optional[str] = None 
    participants_ids : list[int] # ID участников


class PrivateChatOut(ChatBase):
    other_user_id : int 


class GroupChatOut(ChatBase):
    name : str 
    description : Optional[str]
    avatar : Optional[str]
    creator_id : int
    participants_ids : list[int] 


# Схема для обоих типов чатов
class ChatOut(BaseModel):
    id : int 
    type : str
    name : str | None = None
    avatar : str | None = None
    last_message_at : datetime

class GroupChatUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar: Optional[str] = None
    description: Optional[str] = Field(None, min_length=2, max_length=300)
    





    




