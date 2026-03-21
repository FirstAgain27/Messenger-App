from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=15, max_length=15)
    password: str = Field(..., min_length=8, max_length=30)

class Token(BaseModel):
    access_token : str
    token_type : str = "bearer"

