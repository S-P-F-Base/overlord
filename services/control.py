import time
from pathlib import Path

from .types import Service, ServiceStatus


class ServicesControl:
    _services: list[Service] = [
        Service(
            id="game_api",
            name="Игровой API",
            path="/game",
            sock=Path("/run/spf/game_api.sock"),
            public=True,
            maintenance_file=Path("/root/spf/game-api/MAINTENANCE"),
            env_vars=["steam_api"],
        ),
        Service(
            id="wiki",
            name="Википедия",
            path="/wiki",
            sock=Path("/run/spf/wiki.sock"),
            public=True,
            maintenance_file=Path("/root/spf/wiki/MAINTENANCE"),
            env_vars=[],
        ),
        Service(
            id="monolith",
            name="Гиганский шкаф",
            path="/",
            sock=Path("/run/spf/root.sock"),
            public=True,
            maintenance_file=Path("/root/server-spf/MAINTENANCE"),
            env_vars=[],
        ),
    ]

    @classmethod
    def get_all_services(cls) -> list[Service]:
        return cls._services.copy()

    @classmethod
    def get_by_path(cls, path: str) -> Service | None:
        if not path.startswith("/"):
            return None

        for svc in cls._services:
            if svc.path == path:
                return svc

        return None

    @classmethod
    def match(cls, request_path: str) -> Service | None:
        if not request_path.startswith("/"):
            request_path = "/" + request_path

        for svc in cls._services:
            if svc.path != "/" and svc.matches(request_path):
                return svc

        for svc in cls._services:
            if svc.path == "/":
                return svc

        return None

    @classmethod
    def update_status(
        cls,
        svc: Service,
        *,
        status: ServiceStatus,
        reason: str | None = None,
        latency: float | None = None,
    ) -> None:
        svc.status = status
        svc.reason = reason
        svc.latency = latency
        svc.last_check = time.time()
