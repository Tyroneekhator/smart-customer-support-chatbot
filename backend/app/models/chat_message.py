from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    sender = Column(String, nullable=False)  # user or bot
    message = Column(String, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)