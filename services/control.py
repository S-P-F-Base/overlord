# services.py
import time

from .types import Service, ServiceStatus


class ServicesControl:
    _services: list[Service] = [
        {
            "name": "Auth API",
            "path": "/auth",
            "port": 9101,
            "public": True,
            "status": None,
            "reason": None,
            "last_check": None,
            "latency": None,
        },
    ]

    @classmethod
    def get_all_services(cls) -> list[Service]:
        return cls._services.copy()

    @classmethod
    def get_by_path(cls, path: str) -> Service | None:
        if not path.startswith("/"):
            return None

        for svc in cls._services:
            if svc["path"] == path:
                return svc

        return None

    @classmethod
    def match(cls, full_path: str) -> Service | None:
        if not full_path.startswith("/"):
            full_path = "/" + full_path

        for svc in cls._services:
            base = svc["path"]

            if full_path == base:
                return svc

            if full_path.startswith(base + "/"):
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
        svc["status"] = status
        svc["reason"] = reason
        svc["latency"] = latency
        svc["last_check"] = time.time()
