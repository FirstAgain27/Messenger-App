from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime, LargeBinary, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
from ..core.database import cipher

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Храним зашифрованный текст
    encrypted_text = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Для файлов позже добавим
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True)

    @property 
    def text(self):
        if self.encrypted_text:
            return cipher.decrypt(self.encrypted_text).decode()
        return None
    
    @text.setter
    def text(self, plain_text: str):
        """Шифрует текст перед сохранением"""
        if plain_text:
            self.encrypted_text = cipher.encrypt(plain_text.encode())
        else:
            self.encrypted_text = None
        
    

