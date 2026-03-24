from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional 
from datetime import datetime 

# Определяет правила создания объекта класса User
class UserBase(BaseModel):
    phone : str = Field(..., max_length=15, min_length=15, 
                        description="Номер телефона")
    username : str = Field(..., max_length=33, min_length=3)
    first_name : str = Field(..., min_length=2, max_length=25)


class UserCreate(UserBase):
    password : str = Field(..., min_length=8, max_length=30)

class UserOut(UserBase):
    id: int
    email: EmailStr | None = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True) # говорим: можно читать из атрибутов объектов.
                            #Без этой строчки FastAPI не сможет превратить объект из базы в JSON и вывалится с ошибкой.
 
class UserUpdate(BaseModel):
    phone: Optional[str] = Field(None, min_length=15, max_length=15)
    username: Optional[str] = Field(None, min_length=3, max_length=33)
    first_name: Optional[str] = Field(None, min_length=2, max_length=25)
    last_name: Optional[str] = Field(None, max_length=64)
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserDeleteRequest(BaseModel):
    password : str = Field(..., min_length=8, max_length=30) # Вынужденное дублирование, можно поправить после реализации MVP