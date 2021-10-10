from dataclasses import dataclass
from typing import Callable, cast
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.infra.database.repositories import  user_repository


@dataclass(frozen=True)
class Dependencies:
    user_repo: UserRepo


def _build_dependencies() -> Callable[[], Dependencies]:
    deps = Dependencies(
        user_repo=cast(UserRepo, user_repository)
    )

    def fn() -> Dependencies:
        return deps

    return fn


get_dependencies = _build_dependencies()