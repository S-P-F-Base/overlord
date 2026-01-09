from pathlib import Path

from services import ServicesControl


class ENVs:
    SECRETS_FILE = Path("/root/spf/overlord/.env")
    RUNTIME_ENV_DIR = Path("/run/spf/env")

    @classmethod
    def _load_secrets(cls) -> dict[str, str]:
        data: dict[str, str] = {}

        if not cls.SECRETS_FILE.exists():
            return data

        for line in cls.SECRETS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            data[key.strip().lower()] = value.strip()

        return data

    @classmethod
    def _clear_runtime_dir(cls) -> None:
        if not cls.RUNTIME_ENV_DIR.exists():
            return

        for path in cls.RUNTIME_ENV_DIR.iterdir():
            if path.is_file():
                path.unlink()

    @classmethod
    def generate(cls) -> None:
        secrets = cls._load_secrets()

        cls.RUNTIME_ENV_DIR.mkdir(parents=True, exist_ok=True)
        cls._clear_runtime_dir()

        for svc in ServicesControl.get_all_services():
            if not svc.env_vars:
                continue

            lines: list[str] = []

            for key in svc.env_vars:
                value = secrets.get(key.lower())
                if value is not None:
                    lines.append(f"{key}={value}")

            if not lines:
                continue

            env_path = cls.RUNTIME_ENV_DIR / f"{svc.id}.env"
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            env_path.chmod(0o600)
