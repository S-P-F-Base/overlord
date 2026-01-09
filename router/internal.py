from fastapi import APIRouter, HTTPException, Request

from data_control import Constants
from services import ServicesControl

router = APIRouter()


@router.get("/config")
async def overlord_config(request: Request):
    return Constants.get_all_data()


@router.get("/svc/{svc_id}")
async def overlord_svr_id(request: Request, svc_id: str):
    svc = ServicesControl.get_by_id(svc_id)
    if not svc:
        raise HTTPException(status_code=404, detail="service not found")

    return {
        "sock": str(svc.sock),
        "is_usable": bool(svc.status and svc.status.is_usable),
    }
