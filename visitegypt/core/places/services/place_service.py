from typing import Optional, List, Dict
from visitegypt.core.places.entities.place import (
    PlacesPageResponse,
    PlaceInDB,
    UpdatePlace,
    review,
    PlaceBase,
    PlaceForSearch
)
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.core.places.protocols.place_repo import PlaceRepo
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from typing import List, Optional
from visitegypt.core.errors.place_error import PlaceNotFoundError, PlaceAlreadyExists
from visitegypt.core.errors.user_errors import (
    UserNotFoundError,
    PlaceIsAlreadyInFavs,
    PlaceIsNotInFavs
)
async def get_filtered_places(
    repo: PlaceRepo, page_num: int = 1, limit: int = 15, lang: str = 'en', filters: Dict = None
) -> PlacesPageResponse:
    try:
        place_page = await repo.get_filtered_places(page_num=page_num, limit=limit, lang=lang, filters=filters)
        if place_page: return place_page
        raise PlaceNotFoundError
    except PlaceNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e


async def get_all_places_paged(
    repo: PlaceRepo, page_num: int = 1, limit: int = 15, filters: Dict = None
) -> PlacesPageResponse:
    try:
        place = await repo.get_all_places(page_num=page_num, limit=limit, filters=filters)
        if place:
            return place
        raise PlaceNotFoundError
    except PlaceNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e

async def get_some_places(
    repo: PlaceRepo, places_ids
) -> PlacesPageResponse:
    try:
        place = await repo.get_some_places(places_ids)
        if place:
            return place
        raise PlaceNotFoundError
    except PlaceNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e

async def get_places_by_city(
    repo: PlaceRepo, city_name:str,page_num: int = 1, limit: int = 15) -> PlacesPageResponse:
    try:
        place = await repo.get_all_city_places(city_name,page_num, limit)
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

async def get_cities(repo: PlaceRepo) :
    try:
        cities = await repo.get_cities()
        if cities:
            return cities
    except Exception as e:
        raise e

async def get_place_by_title(repo: PlaceRepo, place_title: str) -> Optional[PlaceInDB]:
    try:
        return await repo.get_place_by_title(place_title)
    except PlaceNotFoundError as ue: raise ue
    except Exception as e: raise e

async def create_place(repo: PlaceRepo, new_place: PlaceBase) -> PlaceInDB:
    try:
        place = await repo.get_filtered_places(page_num=1, limit=1, filters={'title': new_place.title})
        if place.places:
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


async def search_places(repo:PlaceRepo, search_str:str) -> Optional[List[PlaceForSearch]]:
    try:
        return await repo.search_place(search_str)
    except Exception as e: raise e


async def add_to_favs(repo: UserRepo, current_user: UserResponse, place_id: str) -> Optional[bool]:
    try:
        return await repo.add_place_to_favs(current_user, place_id)
    except PlaceIsAlreadyInFavs as pia: raise pia
    except UserNotFoundError as ue: raise ue
    except Exception as e: raise e

async def remove_from_favs(repo: UserRepo,  current_user: UserResponse, place_id: str) -> Optional[bool]:
    try:
        return await repo.remove_place_from_favs(current_user, place_id)
    except PlaceIsNotInFavs as pia: raise pia
    except UserNotFoundError as ue: raise ue
    except Exception as e: raise e