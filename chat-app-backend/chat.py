from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessage
from schemas import ChatMessageCreate, ChatMessageRead
from auth import get_current_user
from utils import call_llm
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

MAX_CONTEXT_MESSAGES = 10


@router.post("/message", response_model=ChatMessageRead)
def send_message(
    chat_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info(f"User {current_user.email} sent a message")

    chat = ChatMessage(
        user_id=current_user.id,
        message=chat_in.message,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    logger.debug(f"Message stored with id={chat.id}")

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_CONTEXT_MESSAGES)
        .all()
    )

    logger.debug(f"Loaded {len(history)} messages for context")

    context = "\n".join(
        f"User: {m.message}\nAssistant: {m.response or ''}"
        for m in reversed(history)
    )

    prompt = f"{context}\nUser: {chat_in.message}"

    logger.debug("Calling LLM API")

    chat.response = call_llm(prompt)

    db.commit()
    db.refresh(chat)

    logger.info(f"Response generated for message id={chat.id}")

    return chat


@router.get("/history", response_model=list[ChatMessageRead])
def chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logger.info(f"Fetching chat history for {current_user.email}")

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    logger.debug(f"Returned {len(history)} messages")

    return history