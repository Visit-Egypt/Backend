from ctypes.wintypes import tagRECT
from datetime import datetime
from typing import Optional, List, Dict
from visitegypt.core.errors.place_error import PlaceNotFoundError, ReviewOffensive
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
from visitegypt.infra.database.utils import places_collection_name,users_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next,check_next
from visitegypt.infra.database.utils.offensive import check_offensive
from visitegypt.resources.strings import PLACE_DELETED
from bson import ObjectId
from pymongo import ReturnDocument
from loguru import logger
from visitegypt.infra.errors import InfrastructureException

async def get_filtered_places(
    page_num: int, limit: int, filters: Dict, lang: str = 'en'
) -> PlacesPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][places_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        places_list = await cursor.to_list(limit+1)
        
        """
        lang_en = places_list[0].get('translations').get('en')
        places_list[0].pop('translations')
        places_list[0] = {**places_list[0], **lang_en}
        print(places_list)
        """
        if not places_list:
            raise PlaceNotFoundError
        has_next = len(places_list) > limit
        if len(places_list) > 1: del places_list[-1]
        """
        places_list_response = []
        from visitegypt.infra.database.repositories.tag_repository import get_tags_names_by_id
        for place in places_list:
            # Replace the list of tag ids with the translated tag names.
            tags_names = await get_tags_names_by_id(place['category'], lang)
            place['category'] = tags_names
            places_list_response.append(PlaceInDB.from_mongo(place, lang))
        # print(places_list_response[0].translations)     
        """   
        if not places_list:
            raise PlaceNotFoundError
        document_count = await db.client[DATABASE_NAME][places_collection_name].count_documents(filters)
        places_list_response = [PlaceInDB.from_mongo(place, lang) for place in places_list]
        return PlacesPageResponse(
            current_page=page_num, has_next=has_next, places=places_list_response, content_range=document_count
        )
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_all_places(page_num: int, limit: int, filters: Dict) -> PlacesPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][places_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        places_list = await cursor.to_list(limit+1)
        document_count = await db.client[DATABASE_NAME][places_collection_name].count_documents(filters)
        if not places_list:
            raise PlaceNotFoundError
        places_list_response = [PlaceInDB.from_mongo(place) for place in places_list[:-1]]
        has_next = len(places_list) > limit
        return PlacesPageResponse(
            current_page=page_num, has_next=has_next, places=places_list_response, content_range=document_count
        )
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_some_places(places_ids:List) -> List[PlaceInDB]:
    try:
        cursor = (
            db.client[DATABASE_NAME][places_collection_name].find(
                {"placeActivities.id":{"$in":places_ids}}
        ))
        places_list = await cursor.to_list(length=None)
        if not places_list:
            raise PlaceNotFoundError
        places_list_response = [PlaceInDB.from_mongo(place) for place in places_list]
        return places_list_response
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_place_by_explore(places_ids:List) -> List[PlaceInDB]:
    try:
        cursor = (
            db.client[DATABASE_NAME][places_collection_name].find(
                {"explores.id":{"$in":places_ids}}
        ))
        places_list = await cursor.to_list(length=None)
        if not places_list:
            raise PlaceNotFoundError
        places_list_response = [PlaceInDB.from_mongo(place) for place in places_list]
        return places_list_response
    except PlaceNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_all_city_places(city_name: str,page_num: int, limit: int) -> PlacesPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][places_collection_name]
            .find({"city": city_name})
            .skip(start_index)
            .limit(limit)
        )
        places_list = await cursor.to_list(limit)
        if not places_list:
            raise PlaceNotFoundError
        document_count = await db.client[DATABASE_NAME][places_collection_name].count_documents({"city": city_name})
        places_list_response = [PlaceInDB.from_mongo(place) for place in places_list]
        has_next = check_next(limit,places_list_response)
        return PlacesPageResponse(
            current_page=page_num, has_next=has_next, places=places_list_response, content_range=document_count
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
        created_at = datetime.utcnow()
        row = await db.client[DATABASE_NAME][places_collection_name].insert_one(
            dict(new_place, created_at=created_at, updated_at=created_at)
        )
        if row.inserted_id:
            added_place = await get_filtered_places(page_num = 1, limit = 1, lang = 'en', filters= {"_id" : ObjectId(row.inserted_id)})
            return added_place.places[0]
    except PlaceNotFoundError as ue:
        raise ue
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
        # print(updated_place.dict().items())
        place_witout_translations = updated_place.dict().pop('translations', None)
        result = await db.client[DATABASE_NAME][
            places_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(place_id)},
            {"$set": dict({k: v for k, v in updated_place.dict().items() if v}, updated_at=datetime.utcnow())},
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
        #is_offensive = False
        #if new_reviw.review:
        #    is_offensive = check_offensive(new_reviw.review)
        #if is_offensive:
        #    raise ReviewOffensive
        result = await db.client[DATABASE_NAME][
            places_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(place_id)},
            {"$push": {"reviews": dict(new_reviw, created_at=datetime.utcnow())}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(new_reviw.user_id)},
            {"$set": {"lastReviewd":place_id,"updated_at":datetime.utcnow()}},
        )
            return result["reviews"]
        raise PlaceNotFoundError
    except ReviewOffensive as ro: raise ro
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
    pipeline = [{"$search": {'index': 'title', "wildcard": {"query": search_qu, "path": "title","allowAnalyzedField": True}}}]
    try:
       # row = await db.client[DATABASE_NAME][places_collection_name].find_one(
       #     {"title": place_title}
       # )
        # row = await db.client[DATABASE_NAME][places_collection_name].aggregate(pipeline).to_list(length=None)
        row = await db.client[DATABASE_NAME][places_collection_name].find({'$text': { '$search': search_qu } }).to_list(None)
        if not row:
            return None
        places_list_response = [PlaceForSearch.from_mongo(place) for place in row]
        return places_list_response
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_cities():
    try:
        row = await db.client[DATABASE_NAME][places_collection_name].distinct('city')
        if row:
            return row
        raise Exception
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)