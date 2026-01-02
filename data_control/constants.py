import json
from pathlib import Path


class Constants:
    _data = {}
    _data_path = Path(__file__).parents[1] / "constants.json"

    @classmethod
    def load(cls) -> None:
        if not cls._data_path.exists():
            cls._data.clear()
            return

        try:
            with open(cls._data_path, "r", encoding="utf-8") as file:
                cls._data = json.load(file)

        except Exception:
            cls._data.clear()

    @classmethod
    def get_all_data(cls) -> dict[str, str]:
        return cls._data.copy()
