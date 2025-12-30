from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get("/static/{path:path}")
async def overlord_static(path: str):
    resp = Response(status_code=200)
    resp.headers["X-Accel-Redirect"] = f"/__accel_overlord/{path}"
    return resp
