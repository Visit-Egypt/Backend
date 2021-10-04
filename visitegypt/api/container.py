from dataclasses import dataclass
from typing import Callable, cast

from visitegypt.core.items.protocols.item_repo import ItemRepo
from visitegypt.infra.database.repositories import item_repository


@dataclass(frozen=True)
class Dependencies:
    item_repo: ItemRepo


def _build_dependencies() -> Callable[[], Dependencies]:
    deps = Dependencies(
        item_repo=cast(ItemRepo, item_repository),
    )

    def fn() -> Dependencies:
        return deps

    return fn


get_dependencies = _build_dependencies()