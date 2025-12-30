from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from services import ServicesControl, ServiceStatus
from template_env import templates

router = APIRouter()


def status_to_view(status: ServiceStatus | None) -> dict:
    if status is ServiceStatus.HEALTHY:
        return {"text": "ONLINE", "class": "ok"}

    if status is ServiceStatus.UNHEALTHY:
        return {"text": "OFFLINE", "class": "bad"}

    if status is ServiceStatus.TIMEOUT:
        return {"text": "TIMEOUT", "class": "warn"}

    return {"text": "UNKNOWN", "class": "muted"}


@router.get("/overlord", response_class=HTMLResponse)
async def overlord_page(request: Request):
    services_view = [
        {
            "name": s["name"],
            "path": s["path"],
            "public": s["public"],
            "status": status_to_view(s.get("status")),
            "reason": s.get("reason"),
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
