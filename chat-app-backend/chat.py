from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ChatMessage
from schemas import ChatMessageCreate, ChatMessageRead
from auth import get_current_user
from utils import call_llm

router = APIRouter(tags=["chat"])

MAX_CONTEXT_MESSAGES = 10  # Limit context for scalability


@router.post("/message", response_model=ChatMessageRead)
def send_message(
    chat_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # STEP 4: persist user message first
    chat = ChatMessage(
        user_id=current_user.id,
        message=chat_in.message,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    # STEP B: load recent context
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_CONTEXT_MESSAGES)
        .all()
    )

    # STEP C: build prompt
    context = "\n".join(
        f"User: {m.message}\nAssistant: {m.response or ''}"
        for m in reversed(history)
    )

    prompt = f"{context}\nUser: {chat_in.message}"

    # STEP 5: call LLM
    chat.response = call_llm(prompt)

    # STEP 6: persist response
    db.commit()
    db.refresh(chat)

    # STEP 7: return result
    return chat


@router.get("/history", response_model=list[ChatMessageRead])
def chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
