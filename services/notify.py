import asyncio

import httpx

from .registry import Service, ServicesRegistry

TIMEOUT = 5.0
RETRY_INTERVAL = 5.0


async def notify_one(svc: Service) -> bool:
    try:
        transport = httpx.AsyncHTTPTransport(uds=str(svc.sock))
        async with httpx.AsyncClient(
            transport=transport,
            timeout=TIMEOUT,
        ) as client:
            resp = await client.post("http://service/notify", json={})
            return resp.status_code in (200, 404)

    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False

    except Exception:
        return False


async def notify_services_worker() -> None:
    await asyncio.sleep(1)

    pending = {svc.id: svc for svc in ServicesRegistry.get_all()}

    while pending:
        batch = list(pending.items())
        results = await asyncio.gather(*(notify_one(svc) for _, svc in batch))

        pending = {
            svc_id: svc
            for (svc_id, svc), delivered in zip(batch, results)
            if not delivered
        }

        if pending:
            await asyncio.sleep(RETRY_INTERVAL)
