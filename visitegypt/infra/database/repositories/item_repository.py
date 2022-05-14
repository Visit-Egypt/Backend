from typing import Dict
from visitegypt.core.errors.item_error import ItemNotFoundError
from visitegypt.core.items.entities.item import (
    ItemInDB,
    ItemsPageResponse,
    ItemBase,
    ItemUpdate,
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import items_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next, check_next
from pymongo import ReturnDocument
from bson import ObjectId
from loguru import logger
from visitegypt.infra.errors import InfrastructureException

async def get_filtered_items(
    page_num: int, limit: int, filters: Dict
) -> ItemsPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][items_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        items_list = await cursor.to_list(limit+1)
        if not items_list:
            raise ItemNotFoundError
        document_count = await db.client[DATABASE_NAME][items_collection_name].count_documents(filters)
        items_list_response = [ItemInDB.from_mongo(item) for item in items_list]
        has_next = len(items_list) > limit
        return ItemsPageResponse(
            current_page=page_num, has_next=has_next, items=items_list_response, content_range=document_count
        )
    except ItemNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def create_item(item_to_create: ItemBase) -> ItemInDB:
    try:
        row = await db.client[DATABASE_NAME][items_collection_name].insert_one(
            item_to_create.dict()
        )
        if row.inserted_id:
            new_inserted_item = await get_filtered_items(
                page_num=1, limit=1, filters={"_id": ObjectId(row.inserted_id)}
            )
            return new_inserted_item.items[0]
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_item(item_to_update: ItemUpdate, item_id: str) -> ItemInDB:
    try:
        result = await db.client[DATABASE_NAME][
            items_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": {k: v for k, v in item_to_update.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return ItemInDB.from_mongo(result)
        raise ItemNotFoundError
    except ItemNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def delete_item(item_id: str) -> bool:
    try:
        res = await db.client[DATABASE_NAME][items_collection_name].delete_one(
            {"_id": ObjectId(item_id)}
        )
        if res.deleted_count == 1:
            return True
        raise ItemNotFoundError
    except ItemNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)
