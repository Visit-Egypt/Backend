from typing import Optional, List
from visitegypt.core.tags.entities.tag import Tag, TagUpdate, TagCreation
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import tags_collection_name
from visitegypt.infra.errors import InfrastructureException
from visitegypt.core.errors.tag_error import TagsNotFound, TagCreationError, TagAlreadyExists

from bson import ObjectId
from loguru import logger
from pymongo import ReturnDocument

async def get_all_tags(filter: dict) -> List[Tag]:
    try:
        cursor = db.client[DATABASE_NAME][tags_collection_name].find(filter)
        tags_list = await cursor.to_list(100)
        if not tags_list: raise TagsNotFound
        tags_resp = [Tag.from_mongo(tag) for tag in tags_list]
        return tags_resp
    except TagsNotFound as tagnotfound: raise tagnotfound
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def add_tag(new_tag: TagCreation) -> Optional[Tag]:
    try:
        # Check if the tag already exists
        tag_m = await db.client[DATABASE_NAME][tags_collection_name].find_one({'name': new_tag.name})
        if tag_m: raise TagAlreadyExists
        row = await db.client[DATABASE_NAME][tags_collection_name].insert_one(
            new_tag.dict()
        )
        if row.inserted_id:
            added_tag = await db.client[DATABASE_NAME][tags_collection_name].find_one( {"_id": ObjectId(row.inserted_id)})
            return Tag.from_mongo(added_tag)
        raise TagCreationError
    except TagCreationError as tc: raise tc
    except TagAlreadyExists as tae: raise tae
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_tag(update_tag: TagUpdate, tag_id: str) -> Optional[Tag]:
    try:
        result = await db.client[DATABASE_NAME][
            tags_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(tag_id)},
            {"$set": {k: v for k, v in update_tag.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return Tag.from_mongo(result)
        raise TagsNotFound
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_tag(tag_id: str) -> Optional[bool]:
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
