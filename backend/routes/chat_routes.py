
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.dependencies import get_current_user
from backend.model import ChatMessage

from backend.schemas.schemas import (
    ChatRequest,
    ChatResponse
)

from backend.services.ollama_service import ask_ollama


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ==========================================
# CHAT
# ==========================================

@router.post(
    "/",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    username: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    # --------------------------------------
    # Validate message
    # --------------------------------------

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # --------------------------------------
    # Save user message
    # --------------------------------------

    user_message = ChatMessage(
        username=username,
        role="user",
        content=request.message
    )

    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    # --------------------------------------
    # Get conversation history
    # --------------------------------------

    statement = (
        select(ChatMessage)
        .where(ChatMessage.username == username)
        .order_by(ChatMessage.id)
    )

    previous_messages = session.exec(statement).all()

    # --------------------------------------
    # Prepare messages for Ollama
    # --------------------------------------

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Give clear, accurate and useful answers."
            )
        }
    ]

    # Send only recent messages
    for msg in previous_messages[-20:]:
        messages.append(
            {
                "role": msg.role,
                "content": msg.content
            }
        )

    # --------------------------------------
    # Call Ollama
    # --------------------------------------

    try:

        answer = ask_ollama(messages)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Ollama error: {str(e)}"
        )

    # --------------------------------------
    # Save assistant response
    # --------------------------------------

    assistant_message = ChatMessage(
        username=username,
        role="assistant",
        content=answer
    )

    session.add(assistant_message)
    session.commit()
    session.refresh(assistant_message)

    # --------------------------------------
    # Return response
    # --------------------------------------

    return {
        "response": answer
    }


# ==========================================
# CHAT HISTORY
# ==========================================

@router.get("/history")
def get_history(
    username: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    statement = (
        select(ChatMessage)
        .where(ChatMessage.username == username)
        .order_by(ChatMessage.id)
    )

    messages = session.exec(statement).all()

    return messages


# ==========================================
# DELETE CHAT HISTORY
# ==========================================

@router.delete("/history")
def clear_history(
    username: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    statement = (
        select(ChatMessage)
        .where(ChatMessage.username == username)
    )

    messages = session.exec(statement).all()

    for message in messages:
        session.delete(message)

    session.commit()

    return {
        "message": "Chat history deleted"
    }
