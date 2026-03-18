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

    participants = relationship("ChatParticipant", back_populates="chat")

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


# Модель, объединяющая пользователей и чаты(Many to Many)
class ChatParticipant(Base):
    __tablename__= "chat_participants"

    chat_id = Column(Integer, ForeignKey('chats.id', ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_by_user = Column(Boolean, default=False)

    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="participant")

