import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

def _uuid(): return str(uuid.uuid4())
def _now(): return datetime.now(timezone.utc)

class Character(Base):
    __tablename__ = "characters"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String(100), nullable=False, default="AI助手")
    avatar = Column(String(500), default="")
    system_prompt = Column(Text, nullable=False, default="你是一个友善的AI助手。")
    greeting = Column(String(500), default="你好！")
    temperature = Column(String(10), default="0.8")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)
    conversations = relationship("Conversation", back_populates="character", cascade="all, delete-orphan")
    traits = relationship("UserTrait", back_populates="character", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    title = Column(String(200), default="新对话")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)
    character = relationship("Character", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)
    conversation = relationship("Conversation", back_populates="messages")

class UserTrait(Base):
    __tablename__ = "user_traits"
    id = Column(String, primary_key=True, default=_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    trait_key = Column(String(200), nullable=False)
    trait_value = Column(Text, nullable=False)
    source = Column(String(50), default="ai_extracted")
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)
    character = relationship("Character", back_populates="traits")
