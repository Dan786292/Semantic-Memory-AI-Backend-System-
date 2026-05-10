from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import ChatMessage
from schemas import ChatMessageCreate, ChatMessageRead
from auth import get_current_user

from utils import (
    call_llm,
    text_to_vector,
    cosine_similarity,
    serialize_vector,
    deserialize_vector,
    sanitize_input
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

TOP_K = 5
SHORT_TERM_K = 3


@router.post(
    "/message",
    response_model=ChatMessageRead
)
def send_message(
    chat_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    logger.info(
        f"User {current_user.email} sent message"
    )

    # =========================
    # SANITIZE INPUT
    # =========================

    clean_input = sanitize_input(
        chat_in.message
    )

    # =========================
    # CREATE QUERY EMBEDDING
    # =========================

    query_vector = text_to_vector(
        clean_input
    )

    # =========================
    # SAVE USER MESSAGE
    # =========================

    chat = ChatMessage(
        user_id=current_user.id,
        message=clean_input,
        embedding=serialize_vector(
            query_vector
        )
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    logger.info(
        f"Message stored with id={chat.id}"
    )

    # =========================
    # LOAD USER HISTORY
    # =========================

    all_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id ==
            current_user.id
        )
        .all()
    )

    logger.info(
        f"Loaded {len(all_messages)} messages"
    )

    # =========================
    # SEMANTIC RETRIEVAL
    # =========================

    scored_messages = []

    for msg in all_messages:

        if msg.id == chat.id:
            continue

        if not msg.embedding:
            continue

        try:

            stored_vector = deserialize_vector(
                msg.embedding
            )

            similarity = cosine_similarity(
                query_vector,
                stored_vector
            )

            scored_messages.append(
                (similarity, msg)
            )

        except Exception:

            logger.warning(
                f"Failed loading embedding "
                f"for message {msg.id}"
            )

    # sort by semantic similarity
    scored_messages.sort(
        key=lambda x: x[0],
        reverse=True
    )

    semantic_memories = [
        msg
        for _, msg in scored_messages[:TOP_K]
    ]

    # =========================
    # SHORT TERM MEMORY
    # =========================

    recent_messages = sorted(
        all_messages,
        key=lambda m: m.created_at
    )[-SHORT_TERM_K:]

    # =========================
    # MERGE MEMORIES
    # =========================

    combined = {}

    for msg in (
        semantic_memories +
        recent_messages
    ):
        combined[msg.id] = msg

    final_context_messages = sorted(
        combined.values(),
        key=lambda m: m.created_at
    )

    # =========================
    # BUILD PROMPT
    # =========================

    context = "\n".join(
        (
            f"User: {m.message}\n"
            f"Assistant: {m.response or ''}"
        )
        for m in final_context_messages
    )

    prompt = (
        "You are a helpful AI assistant.\n\n"
        f"{context}\n"
        f"User: {clean_input}"
    )

    logger.info("Sending prompt to LLM")

    # =========================
    # GENERATE RESPONSE
    # =========================

    response = call_llm(prompt)

    chat.response = response

    db.commit()
    db.refresh(chat)

    logger.info(
        f"Generated response "
        f"for message {chat.id}"
    )

    return chat


@router.get(
    "/history",
    response_model=list[ChatMessageRead]
)
def chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    logger.info(
        f"Fetching history for "
        f"{current_user.email}"
    )

    history = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id ==
            current_user.id
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return history