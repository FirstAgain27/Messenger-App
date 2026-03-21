from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.user import UserOut, UserCreate
from schemas.auth import LoginRequest, Token
from repositories.user import UserRepository
from services.user import UserService


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    # 1.Создаем вручную репозиторий и сервис
    user_repo = UserRepository(db)
    user_service = UserService(db, user_repo)
        
    # 2.Дергаем вручную действие, которое хотим совершить с переданными данными
    try:
        user = await user_service.user_register(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # 3. Вовзращаем результат 
    return user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user_service = UserService(db, user_repo)

    user = await user_service.user_authentication(login_data.phone, login_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
