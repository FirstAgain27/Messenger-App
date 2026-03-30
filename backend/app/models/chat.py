from sqlalchemy import Column, Integer, Text, Boolean, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
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
    id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    """Если type = group, то создаем GroupChat, а не просто Chat"""
    __mapper_args__ = {
        "polymorphic_identity" : "group"
    }


# Модель, объединяющая пользователей и чаты(Many to Many)
class ChatParticipant(Base):
    __tablename__= "chat_participants"

    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey('chats.id', ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
 
    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="participant")



