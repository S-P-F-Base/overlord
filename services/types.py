from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ServiceStatus(Enum):
    MAINTENANCE = 0  # сервис в техобслуживании
    TIMEOUT = 1  # за N секунд не ответил
    HEALTHY = 2  # systemd + /ping ок
    UNHEALTHY = 3  # systemd жив, /ping плохой
    STARTING = 4  # systemd запущен, но сервис ещё поднимается


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
