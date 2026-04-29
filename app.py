import contextlib
import platform

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data_control import Constants, ENVs
from router.overlord import router as overlord_router
from template_env import LOCAL_RUN


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    if platform.system() != "Linux":
        raise RuntimeError("Only linux support for overlord for now")

    Constants.load()
    ENVs.generate()

    try:
        yield

    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

if LOCAL_RUN:
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )

app.include_router(overlord_router)
