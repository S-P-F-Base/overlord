from fastapi import APIRouter, HTTPException

from data_control import Constants

router = APIRouter()


@router.get("/config")
async def overlord_config():
    return Constants.get_all_data()


@router.get("/svc/{svc_id}")
async def overlord_svr_id(svc_id: str):
    svc = ServicesRegistry.get_by_id(svc_id)
    if not svc:
        raise HTTPException(status_code=404, detail="service not found")

    return {
        "sock": str(svc.sock),
        "is_usable": bool(svc.status and svc.status.is_usable),
    }
