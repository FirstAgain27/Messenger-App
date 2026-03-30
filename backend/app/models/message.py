from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, LargeBinary, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Chat, User

from core.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), 
        nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    
    # Храним зашифрованный текст (bytes для Fernet)
    encrypted_text: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    # Автоматическое время создания
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Поле для файлов (опциональное)
    file_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("files.id"), 
        nullable=True
    )

    # Рекомендую сразу добавить отношения (Relationships), 
    # чтобы в коде можно было писать message.sender.username
    sender: Mapped["User"] = relationship("User", back_populates="messages")
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

        
    

