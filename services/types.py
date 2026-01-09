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

    status: ServiceStatus | None = None
    reason: str | None = None
    latency: float | None = None
    last_check: float | None = None

    def matches(self, request_path: str) -> bool:
        if self.path == "/":
            return True

        return request_path == self.path or request_path.startswith(self.path + "/")

    def is_in_maintenance(self) -> bool:
        return self.maintenance_file.exists()
