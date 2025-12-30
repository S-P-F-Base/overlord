from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from services import ServicesControl

router = APIRouter()


@router.get("/{svc}/static/{path:path}")
async def service_static(svc: str, path: str):
    service = ServicesControl.get_by_path(f"/{svc}")
    if not service or not service["public"]:
        raise HTTPException(404)

    safe_path = quote(path)

    resp = Response(status_code=200)
    resp.headers["X-Accel-Redirect"] = f"/__accel/{svc}/{safe_path}"
    return resp


# Эйджкейся ибо всё это говно
@router.get("/overlord/static/{path:path}")
async def overlord_static(path: str):
    safe_path = quote(path)

    resp = Response(status_code=200)
    resp.headers["X-Accel-Redirect"] = f"/__accel/overlord/{safe_path}"
    return resp


@router.get("/static/{path:path}")
async def monolith_static(path: str):
    service = ServicesControl.get_by_path("/")
    if not service or not service["public"]:
        raise HTTPException(404)

    safe_path = quote(path)

    resp = Response(status_code=200)
    resp.headers["X-Accel-Redirect"] = f"/__accel/monolith/{safe_path}"
    return resp
