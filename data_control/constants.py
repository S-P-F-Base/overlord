import json
from pathlib import Path


class Constants:
    _data = {}

    OVER_ROOT = Path(__file__).parents[1]
    RUN_DIR = Path("/run/spf")
    OVER_ENV = OVER_ROOT / ".env"
    OVER_CONSTANTS = OVER_ROOT / "constants.json"
    RUNTIME_ENV_DIR = RUN_DIR / "env"
    SERVICES_REPO_PATH = OVER_ROOT / "repo"
    SERVICES_FILE_PATH = Path("/etc/systemd/system")

    @classmethod
    def load(cls) -> None:
        if not cls.OVER_CONSTANTS.exists():
            return

        with open(str(cls.OVER_CONSTANTS), "r", encoding="utf-8") as file:
            cls._data = json.load(file)

    @classmethod
    def get_data(cls) -> dict[str, str]:
        return cls._data.copy()

    @classmethod
    def clear_data(cls) -> None:
        cls._data.clear()
