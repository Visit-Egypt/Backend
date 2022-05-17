from typing import Optional, List
from visitegypt.core.tags.entities.tag import Tag, TagUpdate, TagCreation, GetTagResponse
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import tags_collection_name
from visitegypt.infra.errors import InfrastructureException
from visitegypt.core.errors.tag_error import TagsNotFound, TagCreationError, TagAlreadyExists
from visitegypt.core.accounts.entities.user import UserResponseInTags
from bson import ObjectId
from loguru import logger
from pymongo import ReturnDocument

async def get_all_tags(filter: dict, lang: str) -> List[GetTagResponse]:
    try:
        cursor = db.client[DATABASE_NAME][tags_collection_name].find(filter)
        tags_list = await cursor.to_list(length=None)
        if not tags_list: raise TagsNotFound
        tags_resp = [GetTagResponse.from_mongo(tag, lang) for tag in tags_list]
        return tags_resp
    except TagsNotFound as tagnotfound: raise tagnotfound
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def add_tag(new_tag: TagCreation) -> Optional[GetTagResponse]:
    try:
        # Check if the tag already exists
        tag_m = await db.client[DATABASE_NAME][tags_collection_name].find_one({'name': new_tag.name})
        if tag_m: raise TagAlreadyExists
        row = await db.client[DATABASE_NAME][tags_collection_name].insert_one(
            new_tag.dict()
        )
        if row.inserted_id:
            added_tag = await db.client[DATABASE_NAME][tags_collection_name].find_one( {"_id": ObjectId(row.inserted_id)})
            return GetTagResponse.from_mongo(added_tag)
        raise TagCreationError
    except TagCreationError as tc: raise tc
    except TagAlreadyExists as tae: raise tae
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_tag(update_tag: TagUpdate, tag_id: str) -> Optional[GetTagResponse]:
    try:
        result = await db.client[DATABASE_NAME][
            tags_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(tag_id)},
            {"$set": {k: v for k, v in update_tag.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return GetTagResponse.from_mongo(result)
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_tag(tag_id: str) -> Optional[bool]:
    # On deleting a tag, we need to updates tags in Places, Posts, and Users' interests.
    try:
        res = await db.client[DATABASE_NAME][tags_collection_name].delete_one(
            {"_id": ObjectId(tag_id)}
        )
        if res.deleted_count == 1:
            return True
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_many_tag_users(user_id: str, tag_id: List[ObjectId]):
    try:
        result = await db.client[DATABASE_NAME][
            tags_collection_name
        ].update_many({'_id': {"$in": tag_id}}, {"$addToSet": {"users": ObjectId(user_id)}})
        if result.modified_count == len(tag_id):
            return True
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def remove_many_tag_users(user_id: str, tag_id: List[ObjectId]):
    try:
        result = await db.client[DATABASE_NAME][
            tags_collection_name
        ].update_many({'_id': {"$in": tag_id}}, {"$pull": {"users": ObjectId(user_id)}})
        if result.modified_count == len(tag_id):
            return True
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_all_users_of_tags(tag_ids: List[str]) -> Optional[List[UserResponseInTags]]:
    o_tag = [ObjectId(tag) for tag in tag_ids]
    
    pipeline = [
                    {
                        "$match": {
                        "_id": {
                            "$in": o_tag
                        }
                        }
                    },
                    {
                        "$unwind": "$users"
                    },
                    {
                        "$group": {
                        "_id": None,
                        "data": {
                            "$addToSet": "$users"
                        }
                        }
                    }
                ]
    try:
        result = await db.client[DATABASE_NAME][tags_collection_name].aggregate(pipeline).to_list(length=None)
        if result:
            from visitegypt.infra.database.repositories.user_repository import get_bulk_users_by_id
            users = await get_bulk_users_by_id(result[0].get('data'))
            return users
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)



async def get_tags_names_by_id(tag_ids: List[str], lang: str = 'en') -> List[str]:
    o_tag = [ObjectId(tag) for tag in tag_ids]
    translation_key = f"translations.{lang}.name"
    try:
        result = await db.client[DATABASE_NAME][tags_collection_name].find({'_id': {"$in": o_tag}}, { translation_key: 1 }).to_list(length=None)
        names = []
        if result:
            names = [res.get('translations').get(lang).get('name') for res in result]
            return names
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)
