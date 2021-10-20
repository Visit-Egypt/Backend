from typing import Any


class InfrastructureException(Exception):
    def __init__(self, msg: Any = None) -> None:
        self.msg = msg
