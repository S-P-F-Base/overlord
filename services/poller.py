import asyncio
import errno
import time

import httpx

from services import ServicesControl
from services.types import ServiceStatus

CHECK_INTERVAL = 15.0
TIMEOUT = 5.0


def normalize_connect_error(exc: Exception) -> str:
    cause = getattr(exc, "__cause__", None)
    context = getattr(exc, "__context__", None)

    for err in (cause, context, exc):
        if isinstance(err, OSError):
            if err.errno == errno.ENOENT:
                return "Не удалось запустить сервис"

            if err.errno == errno.ECONNREFUSED:
                return "Сервис не принимает соединение"

            if err.errno == errno.EACCES:
                return "Нет доступа к сокету"

    text = str(exc)

    if "[Errno 2]" in text or "No such file or directory" in text:
        return "Не удалось запустить сервис"

    if "[Errno 111]" in text or "Connection refused" in text:
        return "Сервис не принимает соединение"

    if "[Errno 13]" in text or "Permission denied" in text:
        return "Нет доступа к сокету"

    return text


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

            except httpx.ConnectError as exc:
                ServicesControl.update_status(
                    svc,
                    status=ServiceStatus.UNHEALTHY,
                    reason=normalize_connect_error(exc),
                    latency=None,
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
