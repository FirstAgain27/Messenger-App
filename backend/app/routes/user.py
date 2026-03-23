from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from schemas.user import UserOut, UserUpdate
from models.user import User
from schemas.auth import LoginRequest, Token
from repositories.user import UserRepository
from services.auth import AuthService
from services.user import UserService 

router = APIRouter(prefix='/users', tags=["users"])


@router.patch("/update", response_model=UserOut)
async def update_current_user(
    user_data : UserUpdate, 
    db : AsyncSession = Depends(get_db), 
    current_user : User = Depends(get_current_user)
    ):

    user_repo = UserRepository(db)
    user_service = UserService(db, user_repo)

    try:
        updated_user = await user_service.user_profile_update(user_id=current_user.id,
                                                          user_data=user_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return updated_user