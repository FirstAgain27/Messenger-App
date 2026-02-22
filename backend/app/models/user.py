from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String())
    username = Column(String(33),  unique=True, nullable=False, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)

    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_bot = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_online_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.username}')>"
    
