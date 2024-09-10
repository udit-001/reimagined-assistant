from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api, ui
from app.utils.ai_logger import logger
from app.utils.check_package import is_package_installed


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Loading silero vad models...")
    if is_package_installed("silero_vad"):
        from silero_vad import load_silero_vad

        model = load_silero_vad()
    yield


def create_app():
    app = FastAPI(title="Voicebot API", version="1.0", lifespan=lifespan)

    origins = [
        "http://localhost",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api.router, prefix="/api")
    app.include_router(ui.router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
