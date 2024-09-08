import json
from typing import List

import litellm
from fastapi import HTTPException
from openai import OpenAIError

from app.utils.ai_logger import logger
from config import settings


class LLMService:

    async def chat_completion(self, messages: List[dict[str:str]], step_name: str):
        try:
            stream = await litellm.acompletion(
                model=settings.llm_model_name, messages=messages, stream=True
            )

            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            streamed_response = litellm.stream_chunk_builder(chunks, messages=messages)
            logger.debug(
                f"{step_name}: {json.dumps(json.loads(streamed_response.model_dump_json()), indent=4)}"
            )
        except OpenAIError as e:
            logger.error(f"Error generating LLM response: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        return streamed_response.choices[0].message.content


llm_service = LLMService()
