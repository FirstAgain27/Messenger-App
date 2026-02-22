from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base 

class Chat(Base):
    __tablename__= "chats"

    id = Column(Integer, primary_key=True, index=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String(10), nullable=False)

    """Если type = chat, то создаем обычный Chat"""
    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "chat"
    }

class GroupChat(Chat):
    __tablename__ = "group_chats"

    id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    avatar = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    """Если type = group, то создаем GroupChat, а не просто Chat"""
    __mapper_args__ = {
        "polymorphic_identity" : "group"
    }