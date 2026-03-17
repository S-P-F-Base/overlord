import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ServiceStatus(Enum):
    HEALTHY = 0  # systemd + /ping ок
    MAINTENANCE = 1  # сервис в техобслуживании
    TIMEOUT = 2  # за N секунд не ответил
    UNHEALTHY = 3  # systemd жив, /ping плохой
    STARTING = 4  # systemd запущен, но сервис ещё поднимается

    @property
    def is_usable(self) -> bool:
        return self is ServiceStatus.HEALTHY


@dataclass(slots=True)
class Service:
    id: str
    name: str
    path: str
    sock: Path
    public: bool
    maintenance_file: Path

    env_vars: list[str] = field(default_factory=list)

    status: ServiceStatus = ServiceStatus.STARTING
    reason: str | None = None
    latency: float | None = None
    last_check: float | None = None

    def matches(self, request_path: str) -> bool:
        if self.path == "/":
            return True

        return request_path == self.path or request_path.startswith(self.path + "/")

    def is_in_maintenance(self) -> bool:
        return self.maintenance_file.exists()


class ServicesRegistry:
    _services: list[Service] = [
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
            id="game_api",
            name="Игровой API",
            path="/game",
            sock=Path("/run/spf/game_api.sock"),
            public=True,
            maintenance_file=Path("/root/spf/game-api/MAINTENANCE"),
            env_vars=["STEAM_API"],
        ),
        Service(
            id="dbs",
            name="DBs API",
            path="/dbs",
            sock=Path("/run/spf/dbs.sock"),
            public=False,
            maintenance_file=Path("/root/spf/dbs/MAINTENANCE"),
            env_vars=[],
        ),
        Service(
            id="auth",
            name="API авторизации",
            path="/auth",
            sock=Path("/run/spf/auth.sock"),
            public=True,
            maintenance_file=Path("/root/spf/auth/MAINTENANCE"),
            env_vars=["DISCORD_APP", "STEAM_API", "DISCORD_BOT", "JWT_KEY"],
        ),
        Service(
            id="ds_bot",
            name="DS Bot",
            path="/ds-bot",
            sock=Path("/run/spf/ds-bot.sock"),
            public=False,
            maintenance_file=Path("/root/spf/ds-bot/MAINTENANCE"),
            env_vars=["DISCORD_BOT", "STEAM_API"],
        ),
        Service(
            id="user",
            name="Парель игрока",
            path="/user",
            sock=Path("/run/spf/user.sock"),
            public=True,
            maintenance_file=Path("/root/spf/user/MAINTENANCE"),
            env_vars=["JWT_KEY"],
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
    _by_id: dict[str, Service] = {svc.id: svc for svc in _services}
    _by_path: dict[str, Service] = {svc.path: svc for svc in _services}
    _default_service: Service | None = _by_path.get("/")
    _path_sorted_services: list[Service] = sorted(
        (svc for svc in _services if svc.path != "/"),
        key=lambda svc: len(svc.path),
        reverse=True,
    )

    @staticmethod
    def _normalize_path(path: str) -> str | None:
        if not path:
            return None

        normalized = path if path.startswith("/") else f"/{path}"

        if len(normalized) > 1:
            normalized = normalized.rstrip("/")

        return normalized

    @classmethod
    def get_all(cls) -> list[Service]:
        return cls._services.copy()

    @classmethod
    def get_by_path(cls, path: str) -> Service | None:
        normalized = cls._normalize_path(path)
        if normalized is None:
            return None

        return cls._by_path.get(normalized)

    @classmethod
    def get_by_id(cls, id: str) -> Service | None:
        return cls._by_id.get(id)

    @classmethod
    def match(cls, request_path: str) -> Service | None:
        normalized = cls._normalize_path(request_path)
        if normalized is None:
            return cls._default_service

        for svc in cls._path_sorted_services:
            if svc.matches(normalized):
                return svc

        return cls._default_service

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
