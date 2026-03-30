from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from fastapi import WebSocket

from core.config import settings
from core.database import get_db
from models.user import User
from repositories.user import UserRepository


# --- Хэширование паролей ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- Шифрование сообщений ---
cipher = Fernet(settings.encryption_key.encode())

def encrypt_message(text: str) -> bytes:
    return cipher.encrypt(text.encode())

def decrypt_message(token: bytes) -> str:
    return cipher.decrypt(token).decode()


# Генерация JWT-токена
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Декодирует токен, возвращает объект пользователя из БД
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Реквизиты для входа неверны",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_ws(websocket: WebSocket, token: str = Query(None)):
    # 1. Проверяем, пришел ли токен вообще
    if token is None:
        # Если токена нет, закрываем сокет с кодом "Нарушение политики"
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        # 2. Декодируем токен вручную
        # Мы используем ту же библиотеку jose, что и в обычном коде
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # 3. Извлекаем user_id (обычно он хранится в поле "sub")
        user_id: str = payload.get("sub")
        
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
            
        # Возвращаем ID как целое число
        return int(user_id)

    except (JWTError, ValueError):
        # Если токен подделан, просрочен или ID — не число
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None