from typing import List, Optional
from pydantic import EmailStr
import pymongo
from visitegypt.core.accounts.entities.user import (
    UserResponse,
    UserUpdate,
    User,
    UsersPageResponse,
    Badge
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import (
    users_collection_name,
    calculate_start_index,
    check_has_next,
)
from visitegypt.core.errors.user_errors import UserNotFoundError
from visitegypt.resources.strings import USER_DELETED
from bson import ObjectId
from pymongo import ReturnDocument
from visitegypt.infra.errors import InfrastructureException
from loguru import logger
from fastapi import HTTPException, status
async def create_user(new_user: User) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].insert_one(
            new_user.dict()
        )
        if row.inserted_id:
            return await get_user_by_id(row.inserted_id)
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user(updated_user: UserUpdate, user_id: str) -> Optional[UserResponse]:
    try:
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {k: v for k, v in updated_user.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return UserResponse.from_mongo(result)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user_role(updated_user: str, user_id: str) -> Optional[UserResponse]:
    try:
        if updated_user:
            result = await db.client[DATABASE_NAME][
                users_collection_name
            ].find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"user_role": updated_user}},
                return_document=ReturnDocument.AFTER,
            )
        if result:
            return UserResponse.from_mongo(result)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_user(user_id: str) -> Optional[bool]:
    try:
        res = await db.client[DATABASE_NAME][users_collection_name].delete_one(
            {"_id": ObjectId(user_id)}
        )
        if res.deleted_count == 1:
            return True
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": ObjectId(user_id)}
        )
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_user_by_email(user_email: EmailStr) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"email": user_email}
        )
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except pymongo.errors.OperationFailure as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.details)
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_user_hashed_password(user_id: str) -> str:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": ObjectId(user_id)}
        )
        if row:
            return row["hashed_password"]
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_all_users(page_num: int, limit: int) -> List[UsersPageResponse]:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][users_collection_name]
            .find()
            .skip(start_index)
            .limit(limit)
        )
        users_list = await cursor.to_list(limit)
        if len(users_list) <= 0:
            raise UserNotFoundError
        users_list_response = [UserResponse.from_mongo(user) for user in users_list]
        has_next = await check_has_next(
            start_index, db.client[DATABASE_NAME][users_collection_name]
        )
        return UsersPageResponse(
            current_page=page_num, has_next=has_next, users=users_list_response
        )
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user_tokenID(user_id: str,new_toke_id:str,old_token_id:str=None):
    try:
        if  old_token_id != None:
            await check_user_token(user_id=user_id,token_id=old_token_id)
        await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": new_toke_id}})
    except Exception as e:
        raise e

async def check_user_token(user_id: str,token_id:str) -> UserResponse:
    security_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token ID is please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one(
                {"_id": ObjectId(user_id)}
            )
        
        if  token_id != None and str(user["tokenID"]) !=  token_id:
                await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": "Loged Out"}})
                raise security_exception
        return UserResponse.from_mongo(user)
    except Exception as e:
        raise e

async def user_logout(user_id: str):
    try:
        await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": "Loged Out"}})
    except Exception as e:
        raise e

async def add_badge(user_id: str, new_badge: Badge):
    try:
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$push": {"badges": new_badge.dict()}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return result["badges"]
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)