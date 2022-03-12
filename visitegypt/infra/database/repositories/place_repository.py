from typing import Optional, List
from visitegypt.core.errors.place_error import PlaceNotFoundError
from visitegypt.core.places.entities.place import (
    PlaceInDB,
    PlacesPageResponse,
    PlaceBase,
    UpdatePlace,
    review,
    PlaceForSearch
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import places_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next
from visitegypt.resources.strings import PLACE_DELETED
from bson import ObjectId
from pymongo import ReturnDocument
from loguru import logger
from visitegypt.infra.errors import InfrastructureException


async def get_all_places(page_num: int, limit: int) -> PlacesPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][places_collection_name]
            .find()
            .skip(start_index)
            .limit(limit)
        )
        places_list = await cursor.to_list(limit)
        if not places_list:
            raise PlaceNotFoundError
        places_list_response = [PlaceInDB.from_mongo(place) for place in places_list]
        has_next = await check_has_next(
            start_index, db.client[DATABASE_NAME][places_collection_name]
        )
        return PlacesPageResponse(
            current_page=page_num, has_next=has_next, places=places_list_response
        )
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_place_by_id(place_id: str) -> Optional[PlaceInDB]:
    try:
        row = await db.client[DATABASE_NAME][places_collection_name].find_one(
            {"_id": ObjectId(place_id)}
        )
        if row:
            return PlaceInDB.from_mongo(row)
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_place_by_title(place_title: str) -> Optional[PlaceInDB]:
    try:
        row = await db.client[DATABASE_NAME][places_collection_name].find_one(
            {"title": place_title}
        )
        if row:
            return PlaceInDB.from_mongo(row)
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def create_place(new_place: PlaceBase) -> PlaceInDB:
    try:
        # new_place.reviews = []
        row = await db.client[DATABASE_NAME][places_collection_name].insert_one(
            new_place.dict()
        )
        if row.inserted_id:
            added_place = await get_place_by_id(row.inserted_id)
            return added_place
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)



async def delete_place(place_id: str):
    try:
        res = await db.client[DATABASE_NAME][places_collection_name].delete_one(
            {"_id": ObjectId(place_id)}
        )
        if res.deleted_count == 1:
            return PLACE_DELETED
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def update_place(
    updated_place: UpdatePlace, place_id: str
) -> Optional[PlaceInDB]:
    try:
        result = await db.client[DATABASE_NAME][
            places_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(place_id)},
            {"$set": {k: v for k, v in updated_place.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return PlaceInDB.from_mongo(result)
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)



async def add_review(place_id: str, new_reviw: review):
    try:
        result = await db.client[DATABASE_NAME][
            places_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(place_id)},
            {"$push": {"reviews": new_reviw.dict()}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return result["reviews"]
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def delete_review(place_id: str, review: review):
    try:
        result = await db.client[DATABASE_NAME][
            places_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(place_id)},
            {"$pull": {"reviews": review.dict()}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return result["reviews"]
        raise PlaceNotFoundError
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def search_place(search_text:str) -> Optional[List[PlaceForSearch]]:
    search_qu = f"*{search_text}*"
    pipeline = [{"$search": {"wildcard": {"query": search_qu, "path": "title","allowAnalyzedField": True}}}]
    try:
       # row = await db.client[DATABASE_NAME][places_collection_name].find_one(
       #     {"title": place_title}
       # )
        row = await db.client[DATABASE_NAME][places_collection_name].aggregate(pipeline).to_list(length=None)
        if not row:
            return None
        places_list_response = [PlaceForSearch.from_mongo(place) for place in row]
        return places_list_response
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)