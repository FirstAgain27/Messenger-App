from passlib.context import CryptContext
from cryptography.fernet import Fernet
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# --- Хэширование паролей ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Шифрование сообщений ---
# Инициализируем Fernet один раз при старте
cipher = Fernet(settings.encryption_key.encode())

def encrypt_message(text: str) -> bytes:
    """Шифрует строку и возвращает байты."""
    return cipher.encrypt(text.encode())

def decrypt_message(token: bytes) -> str:
    """Дешифрует байты и возвращает строку."""
    return cipher.decrypt(token).decode()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создание токена для аутентификации"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

