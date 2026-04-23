import subprocess
from pathlib import Path

from .dt import ServiceUnit


class SystemdServicesControl:
    SERVICES_REPO_PATH: Path = None  # pyright: ignore[reportAssignmentType]
    SERVICES_FILE_PATH: Path = Path("/etc/systemd/system")
    SERVICES_ENV_PATH: Path = None  # pyright: ignore[reportAssignmentType]
    RUN_DIR: Path = Path("/run/spf")

    SERVICES_FILE_USER: str = "root"  # bruh
    CPU_AFFINITY = "2 3"
    NICE = 10

    @classmethod
    def _daemon_reload(cls) -> None:
        subprocess.run(
            ["systemctl", "daemon-reload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @classmethod
    def create_service_file(cls, unit: ServiceUnit) -> None:
        """Создание файла сервиса"""

        # setup dirs for safe
        cls.SERVICES_FILE_PATH.mkdir(parents=True, exist_ok=True)
        cls.RUN_DIR.mkdir(parents=True, exist_ok=True)
        # end

        env_unit_path = (
            f"EnvironmentFile={cls.SERVICES_ENV_PATH / f'{unit.id}.env'}"
            if unit.env_vars
            else ""
        )
        code_path = cls.SERVICES_REPO_PATH / unit.id

        payload = f"""[Unit]
Description={unit.name}

[Service]
User={cls.SERVICES_FILE_USER}
WorkingDirectory={code_path}
Environment="PATH={code_path}/.venv/bin"
{env_unit_path}

ExecStart={code_path}/.venv/bin/uvicorn app:app --uds {cls.RUN_DIR}/{unit.id}.sock --workers {unit.workers}

Restart=on-failure
RestartSec=5
CPUAffinity={cls.CPU_AFFINITY}
Nice={cls.NICE}
"""

        unit_path = cls.SERVICES_FILE_PATH / f"spf-{unit.id}.service"
        unit_path.write_text(payload, "utf-8")
        cls._daemon_reload()

    @classmethod
    def start_service(cls, unit: ServiceUnit) -> None:
        subprocess.run(
            ["systemctl", "start", f"spf-{unit.id}.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @classmethod
    def stop_service(cls, unit: ServiceUnit) -> None:
        subprocess.run(
            ["systemctl", "stop", f"spf-{unit.id}.service"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @classmethod
    def remove_service_file(cls, unit: ServiceUnit) -> None:
        """Удаление файла сервиса"""
        path = cls.SERVICES_FILE_PATH / f"spf-{unit.id}.service"

        if path.exists():
            path.unlink()

        cls._daemon_reload()
