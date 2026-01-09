import asyncio
import time

import httpx

from services import ServicesControl, ServiceStatus

CHECK_INTERVAL = 15.0
TIMEOUT = 5.0


async def poll_services() -> None:
    while True:
        for svc in ServicesControl.get_all_services():
            if svc.is_in_maintenance():
                ServicesControl.update_status(
                    svc,
                    status=ServiceStatus.MAINTENANCE,
                    reason="Технические работы",
                    latency=None,
                )
                continue

            start = time.monotonic()

            try:
                transport = httpx.AsyncHTTPTransport(uds=str(svc.sock))

                async with httpx.AsyncClient(
                    transport=transport,
                    timeout=TIMEOUT,
                ) as client:
                    resp = await client.get("http://service/ping")

                latency = time.monotonic() - start

                if resp.status_code == 200:
                    ServicesControl.update_status(
                        svc,
                        status=ServiceStatus.HEALTHY,
                        reason=None,
                        latency=latency,
                    )
                else:
                    ServicesControl.update_status(
                        svc,
                        status=ServiceStatus.UNHEALTHY,
                        reason=f"/ping -> {resp.status_code}",
                        latency=latency,
                    )

            except httpx.TimeoutException:
                ServicesControl.update_status(
                    svc,
                    status=ServiceStatus.TIMEOUT,
                    reason="Ping timeout",
                    latency=None,
                )

            except httpx.HTTPError as exc:
                ServicesControl.update_status(
                    svc,
                    status=ServiceStatus.UNHEALTHY,
                    reason=str(exc),
                    latency=None,
                )

        await asyncio.sleep(CHECK_INTERVAL)
