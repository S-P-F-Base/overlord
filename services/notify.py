import asyncio

import httpx

from services import ServicesControl

TIMEOUT = 5.0
RETRY_INTERVAL = 5.0


async def notify_one(svc):
    try:
        transport = httpx.AsyncHTTPTransport(uds=str(svc.sock))
        async with httpx.AsyncClient(
            transport=transport,
            timeout=TIMEOUT,
        ) as client:
            resp = await client.post("http://service/notify")
            return resp.status_code in (200, 404)

    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
        return False


async def notify_services_worker():
    await asyncio.sleep(1)

    pending = {svc.name: svc for svc in ServicesControl.get_all_services()}

    while pending:
        tasks = {
            name: asyncio.create_task(notify_one(svc)) for name, svc in pending.items()
        }

        for name, task in tasks.items():
            if await task:
                pending.pop(name, None)

        if pending:
            await asyncio.sleep(RETRY_INTERVAL)
