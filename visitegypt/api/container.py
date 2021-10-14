from dataclasses import dataclass
from typing import Callable, cast
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.items.protocols.item_repo import ItemRepo
from visitegypt.infra.database.repositories import  item_repository, user_repository


@dataclass(frozen=True)
class Dependencies:
    user_repo: UserRepo
    item_repo: ItemRepo

def _build_dependencies() -> Callable[[], Dependencies]:
    deps = Dependencies(
        user_repo=cast(UserRepo, user_repository),
        item_repo=cast(ItemRepo, item_repository)
    )

    def fn() -> Dependencies:
        return deps

    return fn


get_dependencies = _build_dependencies()