from enum import Enum
from typing import TypedDict


class ServiceStatus(Enum):
    TIMEOUT = 1  # за 5 секунд сервис не ответил
    HEALTHY = 2  # системд и /ping ответили нормально
    UNHEALTHY = 3  # системд ответил, но не /ping


class Service(TypedDict):
    name: str
    path: str
    port: int
    public: bool

    status: ServiceStatus | None
    reason: str | None

    last_check: float | None
    latency: float | None
