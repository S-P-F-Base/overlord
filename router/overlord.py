from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services import ServicesControl, ServiceStatus
from template_env import templates

router = APIRouter()

_STATUS_DICT = {
    ServiceStatus.MAINTENANCE: {"text": "MAINTENANCE", "class": "warn"},
    ServiceStatus.HEALTHY: {"text": "ONLINE", "class": "ok"},
    ServiceStatus.UNHEALTHY: {"text": "OFFLINE", "class": "bad"},
    ServiceStatus.TIMEOUT: {"text": "TIMEOUT", "class": "warn"},
    None: {"text": "UNKNOWN", "class": "muted"},
}


@router.get("/overlord", response_class=HTMLResponse)
async def overlord_page(request: Request):
    services_view = [
        {
            "name": s.name,
            "path": s.path,
            "public": s.public,
            "status": _STATUS_DICT.get(s.status),
            "reason": s.reason,
        }
        for s in ServicesControl.get_all_services()
    ]

    return templates.TemplateResponse(
        "status.html",
        {
            "request": request,
            "services": services_view,
        },
    )
