from typing import Annotated

from fastapi import Depends, Query

from app.services.chat_session_cache import CHATBOT_CACHE
from app.services.chatbot import Chatbot

from .session_cookie import create_session


async def create_chatbot_session(
    session_id: Annotated[str, Depends(create_session)],
    persona: str = Query(default="Alice", description="The persona to greet"),
) -> Chatbot:
    return CHATBOT_CACHE.get_or_create_session(session_id, persona)
