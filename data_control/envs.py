from services import LIST_OF_SERVICES

from .constants import Constants


class ENVs:
    @classmethod
    def _load_secrets(cls) -> dict[str, str]:
        data: dict[str, str] = {}

        if not Constants.OVER_ENV.exists():
            return data

        for line in Constants.OVER_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            data[key.strip().lower()] = value.strip()

        return data

    @classmethod
    def generate(cls) -> None:
        secrets = cls._load_secrets()

        Constants.RUNTIME_ENV_DIR.mkdir(parents=True, exist_ok=True)

        for svc in LIST_OF_SERVICES:
            if not svc.env_vars:
                continue

            lines: list[str] = []

            for key in svc.env_vars:
                value = secrets.get(key.lower())
                if value is not None:
                    lines.append(f"{key.lower()}={value}")

            if not lines:
                continue

            env_path = Constants.RUNTIME_ENV_DIR / f"{svc.id}.env"
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            env_path.chmod(0o600)
