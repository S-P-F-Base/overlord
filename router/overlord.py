from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from template_env import templates

router = APIRouter()


@router.get("/overlord", response_class=HTMLResponse)
async def overlord_page(request: Request):
    services_view = [
        {
            "name": "TODO",
            "path": "/",
            "public": True,
            "status": {"text": "UNKNOWN", "class": "muted"},
            "reason": "ХЗ",
        }
    ]

    return templates.TemplateResponse(
        request,
        "status.html",
        {"services": services_view},
    )
