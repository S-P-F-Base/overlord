from fastapi import APIRouter, Request

from data_control import Constants, ENVs
from services import ServicesControl

router = APIRouter()


@router.get("/config")
async def overlord_config(request: Request):
    return Constants.get_all_data()


# @router.get("/env")
# async def overlord_env(request: Request):
#     if not request.client or request.client.host != "127.0.0.1":
#         return Response(status_code=403)

#     svr = ServicesControl.get_by_port(request.client.port)
#     if svr is None:
#         return Response(status_code=403)

#     payload = {}

#     for key in svr.env_vars:
#         payload[key] = ENVs.get(key)

#     return payload
