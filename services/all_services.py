from .data_struct import ServiceUnit

LIST_OF_SERVICES = [
    ServiceUnit(
        repo="https://github.com/S-P-F-Base/wiki.git",
        id="wiki",
        name="Википедия",
        workers=1,
        path="/wiki",
        is_root=False,
        is_public=True,
        env_vars=[],
    )
]
