from visitegypt.core.places.entities.place import (
    PlacesPageResponse,
    PlaceInDB,
    UpdatePlace,
    review,
    PlaceBase,
)
from visitegypt.core.places.protocols.place_repo import PlaceRepo
from typing import Optional
from visitegypt.core.errors.place_error import PlaceNotFoundError, PlaceAlreadyExists


async def get_all_places_paged(
    repo: PlaceRepo, page_num: int = 1, limit: int = 15
) -> PlacesPageResponse:
    try:
        place = await repo.get_all_places(page_num, limit)
        if place:
            return place
        raise PlaceNotFoundError
    except PlaceNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e


async def get_place_by_id(repo: PlaceRepo, place_id: str) -> PlaceInDB:
    try:
        place = await repo.get_place_by_id(place_id)
        if place:
            return place
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_place_by_title(repo: PlaceRepo, place_title: str) -> Optional[PlaceInDB]:
    try:
        return await repo.get_place_by_title(place_title)
    except PlaceNotFoundError as ue: raise ue
    except Exception as e: raise e

async def create_place(repo: PlaceRepo, new_place: PlaceBase) -> PlaceInDB:
    try:
        place = await repo.get_place_by_title(new_place.title)
        if place:
            raise PlaceAlreadyExists
    except PlaceAlreadyExists as iee:
        raise iee
    except PlaceNotFoundError:
        pass
    except Exception as e:
        raise e
    try:
        return await repo.create_place(new_place)
    except Exception as e:
        raise e


async def delete_place(repo: PlaceRepo, place_id: str):
    try:
        return await repo.delete_place(place_id)
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def update_place(
    repo: PlaceRepo, place_to_update: UpdatePlace, place_id: str
) -> Optional[PlaceInDB]:
    try:
        return await repo.update_place(place_to_update, place_id)
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def add_review(repo: PlaceRepo, place_id: str, new_reviw: review):
    try:
        place_reviews = await repo.add_review(place_id, new_reviw)
        if place_reviews:
            return place_reviews
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def delete_review(repo: PlaceRepo, place_id: str, review: review):
    try:
        return await repo.delete_review(place_id, review)
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e



