from typing import Dict
from visitegypt.core.errors.badge_error import BadgeNotFoundError
from visitegypt.core.badges.entities.badge import (
    BadgeBase,
    BadgeTask,
    BadgesPageResponse,
    BadgeInDB,
    BadgeUpdate
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import badges_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next,check_next
from pymongo import ReturnDocument
from bson import ObjectId
from loguru import logger
from visitegypt.infra.errors import InfrastructureException
from datetime import datetime

async def get_filtered_badges(
    page_num: int, limit: int, filters: Dict
) -> BadgesPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][badges_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        badges_list = await cursor.to_list(limit+1)
        if not badges_list:
            raise BadgeNotFoundError
        document_count = await db.client[DATABASE_NAME][badges_collection_name].count_documents(filters)
        badges_list_response = [BadgeInDB.from_mongo(badge) for badge in badges_list]
        has_next = len(badges_list) > limit
        return BadgesPageResponse(
            current_page=page_num, has_next=has_next, badges=badges_list_response, content_range=document_count
        )
    except BadgeNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def create_badge(badge_to_create: BadgeBase) -> BadgeInDB:
    try:
        created_at=datetime.utcnow()
        new_badge = dict(badge_to_create.dict(), created_at=created_at, updated_at=created_at)
        row = await db.client[DATABASE_NAME][badges_collection_name].insert_one(
            new_badge
        )
        if row.inserted_id:
            new_inserted_item = await get_filtered_badges(
                page_num=1, limit=1, filters={"_id": row.inserted_id}
            )
            return new_inserted_item.badges[0]
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_badge(badge_to_update: BadgeUpdate, badge_id: str) -> BadgeInDB:
    try:
        updated_at = datetime.utcnow()
        badge_dict = dict({k: v for k, v in badge_to_update.dict().items() if v}, updated_at=updated_at)
        result = await db.client[DATABASE_NAME][
            badges_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(badge_id)},
            {"$set": badge_dict},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return BadgeInDB.from_mongo(result)
        raise BadgeNotFoundError
    except BadgeNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_badge(badge_id: str) -> bool:
    try:
        res = await db.client[DATABASE_NAME][badges_collection_name].delete_one(
            {"_id": ObjectId(badge_id)}
        )
        if res.deleted_count == 1:
            return True
        raise BadgeNotFoundError
    except BadgeNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)