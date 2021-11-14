from dataclasses import dataclass
from typing import Callable, cast
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.items.protocols.item_repo import ItemRepo
from visitegypt.core.places.protocols.place_repo import PlaceRepo
from visitegypt.core.posts.protocols.post_repo import PostRepo
from visitegypt.infra.database.repositories import (
    item_repository,
    user_repository,
    place_repository,
    post_repository
)


@dataclass(frozen=True)
class Dependencies:
    user_repo: UserRepo
    item_repo: ItemRepo
    place_repo: PlaceRepo
    post_repo: PostRepo


def _build_dependencies() -> Callable[[], Dependencies]:
    deps = Dependencies(
        user_repo=cast(UserRepo, user_repository),
        item_repo=cast(ItemRepo, item_repository),
        place_repo=cast(PlaceRepo, place_repository),
        post_repo=cast(PostRepo, post_repository)
    )

    def fn() -> Dependencies:
        return deps

    return fn


get_dependencies = _build_dependencies()
