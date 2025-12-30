import asyncio
import time

import httpx

from services import ServicesControl

from .types import ServiceStatus

CHECK_INTERVAL = 10.0
TIMEOUT = 5.0


async def poll_services() -> None:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        while True:
            for svc in ServicesControl.get_all_services():
                url = f"http://127.0.0.1:{svc.port}/ping"
                start = time.monotonic()

                try:
                    resp = await client.get(url)
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
                            reason=f"/ping вернул {resp.status_code}",
                            latency=latency,
                        )

                except httpx.TimeoutException:
                    ServicesControl.update_status(
                        svc,
                        status=ServiceStatus.TIMEOUT,
                        reason="Превышено время ожидания",
                        latency=None,
                    )

                except httpx.HTTPError:
                    ServicesControl.update_status(
                        svc,
                        status=ServiceStatus.UNHEALTHY,
                        reason="Ошибка при запросе /ping",
                        latency=None,
                    )

            await asyncio.sleep(CHECK_INTERVAL)
