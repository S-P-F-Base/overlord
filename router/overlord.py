from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services import LIST_OF_SERVICES
from template_env import templates

router = APIRouter()


@router.get("/overlord", response_class=HTMLResponse)
async def overlord_page(request: Request):
    services_view = [
        {
            "name": svc.name,
            "path": svc.path,
            "public": svc.is_public,
            "status": {"text": "UNKNOWN", "class": "muted"},
            "reason": "Нихуя не сделан пуллер и обвязка, идите нахуй",
        }
        for svc in LIST_OF_SERVICES
    ]

    return templates.TemplateResponse(
        request,
        "status.html",
        {"services": services_view},
    )
