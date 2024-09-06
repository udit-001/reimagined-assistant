import os
from mimetypes import guess_type

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.dependencies.chatbot_session import create_chatbot_session
from app.services.chatbot import Chatbot
from app.services.persona import personas

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index_page(
    request: Request, chatbot_session: Chatbot = Depends(create_chatbot_session)
):
    response = templates.TemplateResponse(
        request,
        "index.html",
        context={
            "personas": personas,
            "persona": personas[
                request.cookies.get("persona", chatbot_session.persona.name)
            ],
        },
    )
    response.set_cookie(key="session_id", value=chatbot_session.user_id)
    return response


@router.get("/styles.css")
def css_file(request: Request):
    return templates.TemplateResponse(
        request, "styles.css", headers={"Content-Type": "text/css; charset=utf-8"}
    )


@router.get("/script.js")
def js_file(request: Request):
    return templates.TemplateResponse(
        request, "script.js", headers={"Content-Type": "text/javascript; charset=utf-8"}
    )


@router.get("/{file_path:path}")
def image_file(file_path: str):
    base_dir = "app/templates"

    file_path_full = base_dir + "/" + file_path

    if not os.path.exists(file_path_full):
        raise HTTPException(status_code=404, detail="File not found")

    mime_type, _ = guess_type(file_path_full)
    return FileResponse(path=file_path_full, media_type=mime_type, filename=file_path)
