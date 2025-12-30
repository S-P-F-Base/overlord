from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    TIMEOUT = 1  # за 5 секунд сервис не ответил
    HEALTHY = 2  # системд и /ping ответили нормально
    UNHEALTHY = 3  # системд ответил, но не /ping


@dataclass(slots=True)
class Service:
    id: str
    name: str
    path: str
    port: int
    public: bool

    status: ServiceStatus | None = None
    reason: str | None = None
    last_check: float | None = None
    latency: float | None = None

    def matches(self, request_path: str) -> bool:
        if self.path == "/":
            return True

        return request_path == self.path or request_path.startswith(self.path + "/")
