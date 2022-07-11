from datetime import datetime
from typing import Optional, Dict
from visitegypt.core.errors.post_error import PostNotFoundError, PostOffensive
from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import posts_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next,check_next
from visitegypt.infra.database.utils.offensive import check_offensive
from visitegypt.resources.strings import POST_DELETED
from bson import ObjectId
from pymongo import ReturnDocument
from loguru import logger
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.infra.errors import InfrastructureException
from fastapi import HTTPException


async def get_filtered_post(page_num: int, limit: int, filters: Dict = None) -> PostsPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][posts_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        posts_list = await cursor.to_list(limit+1)
        if not posts_list:
            raise PostNotFoundError
        document_count = await db.client[DATABASE_NAME][posts_collection_name].count_documents(filters)
        posts_list_response = [PostInDB.from_mongo(post) for post in posts_list]
        has_next = len(posts_list) > limit
        return PostsPageResponse(
            current_page=page_num, has_next=has_next, posts=posts_list_response, content_range=document_count
        )
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)
"""
async def get_user_posts(page_num: int, limit: int, user_id: str) -> PostsPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][posts_collection_name]
            .find({"user_id": user_id})
            .skip(start_index)
            .limit(limit)
        )
        posts_list = await cursor.to_list(limit)
        
        if not posts_list:
            raise PostNotFoundError
        posts_list_response = [PostInDB.from_mongo(post) for post in posts_list]
        has_next = await check_has_next(
            start_index, db.client[DATABASE_NAME][posts_collection_name]
        )
        
        return PostsPageResponse(
            current_page=page_num, has_next=has_next, posts=posts_list_response
        )
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)
"""
"""
async def get_post_by_id(post_id: str) -> Optional[PostInDB]:
    try:
        row = await db.client[DATABASE_NAME][posts_collection_name].find_one(
            {"_id": ObjectId(post_id)}
        )
        if row:
            return PostInDB.from_mongo(row)
        raise PostNotFoundError
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)
"""

async def create_post(new_post: PostBase) -> Optional[PostInDB]:
    try:
        new_post.likes = []
        #is_offensive = check_offensive(new_post.caption)
        created_at = datetime.utcnow()
        post = dict(new_post, created_at=created_at, updated_at=created_at)
        if True:
            row = await db.client[DATABASE_NAME][posts_collection_name].insert_one(
                post
            )
            if row.inserted_id:
                new_inserted_post = await get_filtered_post(
                    page_num=1, limit=1, filters={"_id": ObjectId(row.inserted_id)}
            )
            return new_inserted_post.posts[0]
        else:
            raise PostOffensive
    except PostOffensive as po: raise po
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_post(post_id: str, user_id:str):
    try:
        post = await db.client[DATABASE_NAME][posts_collection_name].find_one(
            {"_id": ObjectId(post_id)}
        )
        post = PostInDB.from_mongo(post)
        if(post and post.user_id != user_id and user_id != Role.SUPER_ADMIN["name"] and user_id != Role.ADMIN["name"]):
            raise HTTPException(401, detail="Unautherized")

        res = await db.client[DATABASE_NAME][posts_collection_name].delete_one(
            {"_id": ObjectId(post_id)}
        )
        if res.deleted_count == 1:
            return POST_DELETED
        raise PostNotFoundError
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_post(
    updated_post: UpdatePost, post_id: str, user_id: str
) -> Optional[PostInDB]:
    try:
        post = await db.client[DATABASE_NAME][posts_collection_name].find_one(
            {"_id": ObjectId(post_id)}
        )
        post = PostInDB.from_mongo(post)
        if(post and post.user_id != user_id):
            print(post.user_id + user_id)
            raise HTTPException(401, detail="Unautherized")
        
        updated_at = datetime.utcnow()
        updated_post11 = dict({k: v for k, v in updated_post.dict().items() if v}, updated_at=updated_at)
        result = await db.client[DATABASE_NAME][
            posts_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$set": updated_post11},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return PostInDB.from_mongo(result)
        raise PostNotFoundError
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def add_like(post_id: str,user_id:str):
    try:
        result = await db.client[DATABASE_NAME][
            posts_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": user_id}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return result["likes"]
        raise PostNotFoundError
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_like(post_id: str,user_id:str):
    try:
        result = await db.client[DATABASE_NAME][
            posts_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": user_id}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return result["likes"]
        raise PostNotFoundError
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)