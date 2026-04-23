from dataclasses import dataclass
from enum import IntEnum, auto


class ServiceUnitStatus(IntEnum):
    NO_INFO = 0
    NOT_INSTALL = auto()


@dataclass
class ServiceUnit:
    repo: str

    id: str
    name: str
    desc: str
    workers: int

    path: str
    is_root: bool
    is_public: bool

    env_vars: list[str]

    # runtime vars
    status: ServiceUnitStatus = ServiceUnitStatus.NO_INFO
