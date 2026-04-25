import json
from pathlib import Path

OVER_ROOT = Path(__file__).parents[1]
RUN_DIR = Path("/run/spf")


class Constants:
    _data = {}

    OVER_ENV = OVER_ROOT / ".env"
    OVER_CONSTANTS = OVER_ROOT / "constants.json"
    RUNTIME_ENV_DIR = RUN_DIR / "env"
    SERVICES_REPO_PATH: Path = OVER_ROOT / "repo"
    SERVICES_FILE_PATH: Path = Path("/etc/systemd/system")

    @classmethod
    def load(cls) -> None:
        if not cls.OVER_CONSTANTS.exists():
            cls._data.clear()
            return

        try:
            with open(cls.OVER_CONSTANTS, "r", encoding="utf-8") as file:
                cls._data = json.load(file)

        except Exception:
            cls._data.clear()

    @classmethod
    def get_all_data(cls) -> dict[str, str]:
        return cls._data.copy()
