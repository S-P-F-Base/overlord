import asyncio
import contextlib
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data_control import Constants, ENVs
from router.internal import router as internal_router
from router.overlord import router as overlord_router
from router.proxy import router as proxy_router
from router.static_accel import router as static_accel_router
from services import notify_services_worker, poll_services_worker


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    poll_task = asyncio.create_task(poll_services_worker())
    notify_task = asyncio.create_task(notify_services_worker())

    Constants.load()
    ENVs.generate()

    try:
        yield

    finally:
        poll_task.cancel()
        notify_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await poll_task
            await notify_task


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

if os.getenv("FASTAPISTATIC") == "1":
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )

app.include_router(overlord_router)
app.include_router(internal_router)
app.include_router(static_accel_router)
app.include_router(proxy_router)
