from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from schemas.user import UserOut, UserUpdate, UserDeleteRequest
from models.user import User
from repositories.user import UserRepository
from services.user import UserService 


router = APIRouter(prefix='/api/messages')
