from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from services import ServicesControl

router = APIRouter()


@router.get("/{svc}/static/{path:path}")
async def service_static(svc: str, path: str):
    service = ServicesControl.get_by_path(f"/{svc}")
    if not service or not service["public"]:
        raise HTTPException(404)

    resp = Response(status_code=200)
    resp.headers["X-Accel-Redirect"] = f"/__accel/{svc}/{path}"
    return resp
