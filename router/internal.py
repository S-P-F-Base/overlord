from fastapi import APIRouter, Request

from data_control import Constants

router = APIRouter()


@router.get("/config")
async def overlord_config(request: Request):
    return Constants.get_all_data()
