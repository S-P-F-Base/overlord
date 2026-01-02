from pathlib import Path


class ENVs:
    _data = {}
    _env_path = Path(__file__).parents[1] / ".env"

    @classmethod
    def load(cls) -> None:
        cls._data.clear()

        if not cls._env_path.exists():
            return

        for line in cls._env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            cls._data[key.strip()] = value.strip()

    @classmethod
    def get(cls, key: str, default: str | None = None) -> str | None:
        return cls._data.get(key, default)
