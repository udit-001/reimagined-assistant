from uuid import uuid4

from fastapi import Request

from app.services.chatbot import Chatbot


async def create_session(request: Request) -> Chatbot:
    session_id = request.cookies.get("session_id")
    if session_id == None:
        session_token = uuid4()
        session_id = session_token
    return session_id
