from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models.chat_message import ChatMessage
from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatSessionResponse
)
from app.services.chatbot_service import ChatbotService


router = APIRouter(
    prefix="/api/chat",
    tags=["Chatbot"]
)

chatbot_service = ChatbotService()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    return chatbot_service.process_message(
        db=db,
        user_message=request.message,
        session_id=request.session_id
    )


@router.get("/history/{session_id}", response_model=List[ChatMessageResponse])
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    if not messages:
        raise HTTPException(
            status_code=404,
            detail="No chat history found for this session."
        )

    return messages


@router.delete("/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .all()
    )

    if not messages:
        raise HTTPException(
            status_code=404,
            detail="No chat history found for this session."
        )

    for message in messages:
        db.delete(message)

    db.commit()

    return {
        "message": "Chat history deleted successfully.",
        "session_id": session_id
    }


@router.get("/sessions/recent", response_model=List[ChatSessionResponse])
def get_recent_chat_sessions(db: Session = Depends(get_db)):
    latest_message_subquery = (
        db.query(
            ChatMessage.session_id,
            func.max(ChatMessage.created_at).label("last_message_time")
        )
        .group_by(ChatMessage.session_id)
        .subquery()
    )

    sessions = (
        db.query(ChatMessage)
        .join(
            latest_message_subquery,
            (ChatMessage.session_id == latest_message_subquery.c.session_id)
            & (ChatMessage.created_at == latest_message_subquery.c.last_message_time)
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
    )

    results = []

    for session in sessions:
        total_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session.session_id)
            .count()
        )

        results.append(
            {
                "session_id": session.session_id,
                "total_messages": total_messages,
                "last_message": session.message,
                "last_message_time": session.created_at
            }
        )

    return results