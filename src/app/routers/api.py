import os
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse

from app.dependencies.chatbot_session import create_chatbot_session
from app.services.chatbot import Chatbot
from config import settings

from ..utils.ai_logger import logger as ai_logger

router = APIRouter()


def remove_headers(raw_bytes):
    header_boundary = b"\r\n\r\n"
    if header_boundary in raw_bytes:
        return raw_bytes.split(header_boundary)[1]
    else:
        return raw_bytes


@router.post("/upload_stream")
async def upload_audio_stream(
    request: Request, chatbot: Chatbot = Depends(create_chatbot_session, use_cache=True)
):
    audio_data = []

    async for chunk in request.stream():
        audio_data.append(chunk)

    output_filename = await process_audio_data(audio_data, chatbot=chatbot)
    response = FileResponse(output_filename, media_type="audio/mpeg")
    if request.cookies.get("persona") != chatbot.persona.name:
        response.set_cookie(key="persona", value=chatbot.persona.name)
    return response


async def process_audio_data(audio_data: List[bytes], chatbot: Chatbot):
    combined_audio = b"".join(audio_data)
    return await save_and_process_audio(combined_audio, chatbot=chatbot)


async def save_and_process_audio(audio_bytes: bytes, chatbot: Chatbot):
    cleaned_data = remove_headers(audio_bytes)

    input_filename = f"{settings.media_path}/temp_audio-{chatbot.user_id}.ogg"
    async with aiofiles.open(input_filename, "wb") as f:
        ai_logger.debug(f"Saving user's audio to {input_filename}")
        await f.write(cleaned_data)

    output_filename = await chatbot.voice_respond(input_filename)

    return output_filename
