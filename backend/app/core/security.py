from passlib.context import CryptContext
from cryptography.fernet import Fernet
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