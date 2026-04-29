import subprocess

from data_control.constants import RUN_DIR, Constants

from .data_struct import ServiceUnit


class SystemdServicesControl:
    SERVICES_FILE_USER: str = "root"  # bruh
    CPU_AFFINITY = "2 3"
    NICE = 10

    @classmethod
    def daemon_reload(cls) -> None:
        subprocess.run(
            ["systemctl", "daemon-reload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @classmethod
    def create_service_file(cls, unit: ServiceUnit) -> None:
        """Создание файла сервиса"""

        # setup dirs for safe
        Constants.SERVICES_FILE_PATH.mkdir(parents=True, exist_ok=True)
        RUN_DIR.mkdir(parents=True, exist_ok=True)

        code_path = Constants.SERVICES_REPO_PATH / unit.id
        env_unit_path = (
            f"EnvironmentFile={Constants.RUNTIME_ENV_DIR / f'{unit.id}.env'}"
            if unit.env_vars
            else ""
        )

        payload = f"""\
[Unit]
Description={unit.name}

[Service]
User={cls.SERVICES_FILE_USER}
WorkingDirectory={code_path}
Environment="PATH={code_path}/.venv/bin"
{env_unit_path}

ExecStart={code_path}/.venv/bin/uvicorn app:app --uds {RUN_DIR}/{unit.id}.sock --workers {unit.workers}

Restart=on-failure
RestartSec=5
CPUAffinity={cls.CPU_AFFINITY}
Nice={cls.NICE}
"""

        unit_path = Constants.SERVICES_FILE_PATH / f"spf-{unit.id}.service"
        unit_path.write_text(payload, "utf-8")

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
        path = Constants.SERVICES_FILE_PATH / f"spf-{unit.id}.service"

        if path.exists():
            path.unlink()
