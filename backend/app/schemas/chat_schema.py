from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    session_id: str


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    sender: str
    message: str
    intent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    session_id: str
    total_messages: int
    last_message: str
    last_message_time: datetime