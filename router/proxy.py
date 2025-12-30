import time

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from services import ServicesControl
from services.types import ServiceStatus
from template_env import templates

router = APIRouter()

HOP_BY_HOP_HEADERS: set[str] = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept.lower()


async def forward_request(
    request: Request,
    *,
    service,
    host: str,
    port: int,
    timeout: float = 5.0,
) -> tuple[httpx.Response, Response]:
    url = f"http://{host}:{port}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"

    body = await request.body()

    headers = {
        k: v for k, v in request.headers.items() if k.lower() not in HOP_BY_HOP_HEADERS
    }

    if request.client:
        headers["x-forwarded-for"] = request.client.host
        headers["x-real-ip"] = request.client.host

    start = time.monotonic()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            upstream_resp = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
            )

        latency = time.monotonic() - start

        ServicesControl.update_status(
            service,
            status=ServiceStatus.HEALTHY,
            latency=latency,
        )

    except httpx.ConnectError:
        ServicesControl.update_status(
            service,
            status=ServiceStatus.UNHEALTHY,
            reason="connect error",
        )
        raise HTTPException(502, "Сервис недоступен")

    except httpx.TimeoutException:
        ServicesControl.update_status(
            service,
            status=ServiceStatus.TIMEOUT,
            reason="timeout",
        )
        raise HTTPException(504, "Сервис не ответил вовремя")

    except httpx.HTTPError:
        ServicesControl.update_status(
            service,
            status=ServiceStatus.UNHEALTHY,
            reason="http error",
        )
        raise HTTPException(502, "Получен некорректный ответ от сервиса")

    response_headers = {
        k: v
        for k, v in upstream_resp.headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS
    }

    proxy_resp = Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=response_headers,
        media_type=upstream_resp.headers.get("content-type"),
    )

    return upstream_resp, proxy_resp


@router.api_route("/{full_path:path}", methods=["GET", "POST"])
async def proxy(full_path: str, request: Request):
    service = ServicesControl.match(f"/{full_path}")
    if not service or not service["public"]:
        raise HTTPException(404)

    try:
        upstream_resp, resp = await forward_request(
            request,
            service=service,
            host="127.0.0.1",
            port=service["port"],
        )

    except HTTPException as exc:
        if wants_html(request):
            return templates.TemplateResponse(
                f"errors/{exc.status_code}.html",
                {
                    "request": request,
                    "service": service,
                    "reason": exc.detail,
                },
                status_code=exc.status_code,
            )
        raise

    upstream_ct = upstream_resp.headers.get("content-type", "")

    if upstream_ct.startswith("application/json"):
        return resp

    if service["path"] == "/" and wants_html(request):
        return resp

    if wants_html(request) and resp.status_code in {403, 404, 500, 502}:
        reason = None

        try:
            data = upstream_resp.json()
            if isinstance(data, dict):
                reason = data.get("detail") or data.get("error") or data.get("message")

        except Exception:
            pass

        return templates.TemplateResponse(
            f"errors/{resp.status_code}.html",
            {
                "request": request,
                "service": service,
                "path": request.url.path,
                "reason": reason,
            },
            status_code=resp.status_code,
        )

    return resp
