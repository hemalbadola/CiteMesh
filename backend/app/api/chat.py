from datetime import datetime
from typing import Any, List, Optional, TYPE_CHECKING, cast

import json
import os

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc
from sqlmodel import Session, func, select

from ..core.api_key_rotator import get_a4f_key, get_gemini_key
from ..core.firebase_auth import FirebaseUser, get_current_user
from ..db import get_session as get_db_session
from ..models import ResearchChatMessage, ResearchChatSession, User

router = APIRouter()

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql.schema import Table

SessionTable = cast("Table", getattr(ResearchChatSession, "__table__"))
MessageTable = cast("Table", getattr(ResearchChatMessage, "__table__"))

# Pydantic Models
class CreateSessionRequest(BaseModel):
    """Request to create a new chat session"""
    title: str = Field(..., min_length=1, max_length=200)
    model: str = Field(default="gemini", description="Model to use: gemini or a4f")
    system_prompt: Optional[str] = Field(None, max_length=2000, description="Optional system prompt")

class UpdateSessionRequest(BaseModel):
    """Request to update a chat session"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    system_prompt: Optional[str] = Field(None, max_length=2000)

class SendMessageRequest(BaseModel):
    """Request to send a message in a chat session"""
    content: str = Field(..., min_length=1, max_length=5000)
    paper_references: Optional[List[str]] = Field(None, description="List of paper IDs to reference")
    use_context: bool = Field(True, description="Use previous messages as context")
    model: str = Field(default="gemini", description="Model to use: gemini or a4f")

class MessageResponse(BaseModel):
    """Chat message response"""
    id: int
    session_id: int
    role: str
    content: str
    paper_references: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime

class SessionResponse(BaseModel):
    """Chat session response"""
    id: int
    user_id: int
    title: str
    model: str
    message_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class SessionWithMessagesResponse(SessionResponse):
    """Chat session with messages"""
    messages: List[MessageResponse]


def _extract_scalar(result: Optional[Any]) -> int:
    """Normalize scalar query results across SQLAlchemy versions."""
    if result is None:
        return 0

    extracted: Any = result
    try:
        extracted = result[0]  # type: ignore[index]
    except (TypeError, KeyError, IndexError, AttributeError):
        extracted = result

    if extracted is None:
        return 0

    if isinstance(extracted, (int, float)):
        return int(extracted)

    if isinstance(extracted, str):
        try:
            return int(extracted)
        except ValueError:
            return 0

    return 0


def call_gemini_api(messages: List[dict], system_prompt: Optional[str] = None) -> str:
    """
    Call Gemini API with message history
    """
    api_key = get_gemini_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="Gemini API service unavailable")
    
    # Build prompt with context
    full_prompt = ""
    if system_prompt:
        full_prompt += f"System: {system_prompt}\n\n"
    
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role}: {msg['content']}\n\n"
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048,
                    "topP": 0.8,
                    "topK": 40
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return text
            else:
                raise HTTPException(status_code=500, detail="No response from Gemini")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Gemini API error: {response.text}")
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Gemini API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


def call_a4f_api(messages: List[dict], system_prompt: Optional[str] = None) -> str:
    """
    Call A4F API with message history
    """
    api_key = get_a4f_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="A4F API service unavailable")
    
    base_url = os.getenv("A4F_BASE_URL", "https://api.a4f.co/v1")
    model = os.getenv("A4F_MODEL", "provider-5/gpt-4o-mini")
    
    # Build messages array
    api_messages = []
    if system_prompt:
        api_messages.append({"role": "system", "content": system_prompt})
    
    for msg in messages:
        api_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": api_messages,
                "temperature": 0.7,
                "max_tokens": 2048
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise HTTPException(status_code=500, detail="No response from A4F")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"A4F API error: {response.text}")
            
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="A4F API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A4F error: {str(e)}")


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Create a new chat session
    """
    if current_user.db_user.id is None:
        raise HTTPException(status_code=400, detail="User must be saved to database first")
    
    try:
        chat_session = ResearchChatSession(
            user_id=current_user.db_user.id,
            title=request.title,
            system_prompt=request.system_prompt
        )
        
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        
        return SessionResponse(
            id=cast(int, chat_session.id),
            user_id=chat_session.user_id,
            title=chat_session.title,
            model=request.model,
            message_count=0,
            last_message_at=None,
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = 50,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    List all chat sessions for a user
    """
    if current_user.db_user.id is None:
        return []
    
    statement = (
        select(ResearchChatSession)
        .where(ResearchChatSession.user_id == current_user.db_user.id)
        .order_by(desc(SessionTable.c.updated_at))
        .limit(limit)
    )
    
    sessions = session.exec(statement).all()
    
    # Count messages for each session
    results = []
    for chat_session in sessions:
        msg_count_row = session.exec(
            select(func.count(MessageTable.c.id))
            .where(ResearchChatMessage.session_id == chat_session.id)
        ).first()
        msg_count = _extract_scalar(msg_count_row)
        
        # Get last message timestamp
        last_msg = session.exec(
            select(ResearchChatMessage)
            .where(ResearchChatMessage.session_id == chat_session.id)
            .order_by(desc(MessageTable.c.created_at))
            .limit(1)
        ).first()
        
        results.append(SessionResponse(
            id=cast(int, chat_session.id),
            user_id=chat_session.user_id,
            title=chat_session.title,
            model="gemini",  # Default
            message_count=msg_count,
            last_message_at=last_msg.created_at if last_msg else None,
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at
        ))
    
    return results


@router.get("/sessions/{session_id}", response_model=SessionWithMessagesResponse)
async def get_session(
    session_id: int,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Get a chat session with all its messages
    """
    chat_session = session.get(ResearchChatSession, session_id)
    
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if chat_session.user_id != current_user.db_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all messages
    messages = session.exec(
        select(ResearchChatMessage)
        .where(ResearchChatMessage.session_id == session_id)
        .order_by(asc(MessageTable.c.created_at))
    ).all()
    
    message_responses = [
        MessageResponse(
            id=cast(int, msg.id),
            session_id=msg.session_id,
            role=msg.sender,
            content=msg.content,
            paper_references=msg.references,
            token_count=None,
            created_at=msg.created_at
        )
        for msg in messages
        if msg.id is not None
    ]
    
    return SessionWithMessagesResponse(
        id=cast(int, chat_session.id),
        user_id=chat_session.user_id,
        title=chat_session.title,
        model="gemini",
        message_count=len(messages),
        last_message_at=messages[-1].created_at if messages else None,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        messages=message_responses
    )


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    request: UpdateSessionRequest,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Update a chat session
    """
    chat_session = session.get(ResearchChatSession, session_id)
    
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if chat_session.user_id != current_user.db_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if request.title is not None:
        chat_session.title = request.title
    if request.system_prompt is not None:
        chat_session.system_prompt = request.system_prompt
    
    chat_session.updated_at = datetime.utcnow()
    
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    
    # Count messages
    msg_count_row = session.exec(
        select(func.count(MessageTable.c.id))
        .where(ResearchChatMessage.session_id == session_id)
    ).first()
    msg_count = _extract_scalar(msg_count_row)
    
    return SessionResponse(
        id=cast(int, chat_session.id),
        user_id=chat_session.user_id,
        title=chat_session.title,
        model="gemini",
        message_count=msg_count,
        last_message_at=None,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Delete a chat session and all its messages
    """
    chat_session = session.get(ResearchChatSession, session_id)
    
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if chat_session.user_id != current_user.db_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete all messages first
    messages = session.exec(
        select(ResearchChatMessage)
        .where(ResearchChatMessage.session_id == session_id)
    ).all()
    
    for msg in messages:
        session.delete(msg)
    
    # Delete session
    session.delete(chat_session)
    session.commit()
    
    return {"message": "Session deleted successfully"}


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Send a message in a chat session and get AI response
    """
    chat_session = session.get(ResearchChatSession, session_id)
    
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if chat_session.user_id != current_user.db_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Save user message
    user_message = ResearchChatMessage(
        session_id=session_id,
        sender="user",
        content=request.content,
        references=json.dumps(request.paper_references) if request.paper_references else None
    )
    
    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    if user_message.id is None:
        raise HTTPException(status_code=500, detail="Failed to persist user message")
    user_message_id = cast(int, user_message.id)
    
    # Get context if requested
    context_messages = []
    if request.use_context:
        prev_messages = session.exec(
            select(ResearchChatMessage)
            .where(ResearchChatMessage.session_id == session_id)
            .where(MessageTable.c.id < user_message_id)
            .order_by(desc(MessageTable.c.created_at))
            .limit(10)
        ).all()
        
        # Reverse to chronological order
        for msg in reversed(prev_messages):
            context_messages.append({
                "role": msg.sender,
                "content": msg.content
            })
    
    # Add current message
    context_messages.append({
        "role": "user",
        "content": request.content
    })
    
    # Call AI API
    try:
        if request.model == "a4f":
            ai_response = call_a4f_api(context_messages, chat_session.system_prompt)
        else:
            ai_response = call_gemini_api(context_messages, chat_session.system_prompt)
        
        # Save AI response
        assistant_message = ResearchChatMessage(
            session_id=session_id,
            sender="assistant",
            content=ai_response,
            references=None
        )
        
        session.add(assistant_message)
        
        # Update session timestamp
        chat_session.updated_at = datetime.utcnow()
        session.add(chat_session)
        
        session.commit()
        session.refresh(assistant_message)

        if assistant_message.id is None:
            raise HTTPException(status_code=500, detail="Failed to persist assistant message")
        
        return MessageResponse(
            id=cast(int, assistant_message.id),
            session_id=assistant_message.session_id,
            role=assistant_message.sender,
            content=assistant_message.content,
            paper_references=assistant_message.references,
            token_count=None,
            created_at=assistant_message.created_at
        )
        
    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"AI response error: {str(e)}")


@router.get("/stats")
async def get_chat_stats(
    session: Session = Depends(get_db_session),
    current_user: FirebaseUser = Depends(get_current_user)
):
    """
    Get chat statistics for a user
    """
    if current_user.db_user.id is None:
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "last_chat_at": None
        }
    
    # Count sessions
    session_count_row = session.exec(
        select(func.count(SessionTable.c.id))
        .where(ResearchChatSession.user_id == current_user.db_user.id)
    ).first()
    session_count = _extract_scalar(session_count_row)
    
    # Count total messages
    message_count_row = session.exec(
        select(func.count(MessageTable.c.id))
        .join(ResearchChatSession)
        .where(ResearchChatSession.user_id == current_user.db_user.id)
    ).first()
    message_count = _extract_scalar(message_count_row)
    
    # Get most recent session
    recent_session = session.exec(
        select(ResearchChatSession)
        .where(ResearchChatSession.user_id == current_user.db_user.id)
        .order_by(desc(SessionTable.c.updated_at))
        .limit(1)
    ).first()
    
    return {
        "total_sessions": session_count,
        "total_messages": message_count,
        "last_chat_at": recent_session.updated_at.isoformat() if recent_session else None
    }
