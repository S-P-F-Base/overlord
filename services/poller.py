import asyncio
import time

import httpx

from services import ServicesControl

from .types import ServiceStatus

CHECK_INTERVAL = 15.0
TIMEOUT = 5.0


async def poll_services() -> None:
    transport = httpx.AsyncHTTPTransport(uds="/run/spf/overlord.sock")

    async with httpx.AsyncClient(
        transport=transport,
        timeout=TIMEOUT,
    ) as client:
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
                    resp = await client.get(f"http://{svc.id}/ping")
                    latency = time.monotonic() - start

                    if resp.status_code == 200:
                        ServicesControl.update_status(
                            svc,
                            status=ServiceStatus.HEALTHY,
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

                except httpx.HTTPError as e:
                    ServicesControl.update_status(
                        svc,
                        status=ServiceStatus.UNHEALTHY,
                        reason=str(e),
                        latency=None,
                    )

            await asyncio.sleep(CHECK_INTERVAL)
