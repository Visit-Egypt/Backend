from typing import Optional
from bson.objectid import _raise_invalid_id
from loguru import logger
from pydantic import EmailStr
from fastapi import HTTPException
from visitegypt.core.accounts.entities.user import UserResponse, UserInDB, UserUpdate, User,UserUpdaterole,UsersResponse
from visitegypt.core.accounts.services.hash_service import get_password_hash
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import users_collection_name
from pymongo.results import DeleteResult
from visitegypt.core.errors.user_errors import UserNotFoundError
from visitegypt.resources.strings import USER_DELETED
from bson import ObjectId
from typing import List
from bson.json_util import dumps, loads

async def create_user(new_user: User) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].insert_one(new_user.dict())
        if row.inserted_id:
            return await get_user_by_id(row.inserted_id)
    except Exception as e:
        raise e

async def update_user(updated_user: UserUpdate,user_id:str) -> Optional[UserResponse] : 
    try:
        if updated_user.email:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"email": updated_user.email}})
        if updated_user.first_name:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"first_name": updated_user.first_name}})
        if updated_user.last_name:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"last_name": updated_user.last_name}})
        if updated_user.phone_number:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"phone_number": updated_user.phone_number}})
        if updated_user.password:
            password_hash = get_password_hash(updated_user.password)
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"password": password_hash}})
        if result.modified_count == 1:
            row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def update_user_role(updated_user: str,user_id:str) -> Optional[UserResponse]: 
    try:
        if updated_user:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"user_role": updated_user}})
        if result.modified_count == 1:
            row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def delete_user(user_id: str) -> Optional[DeleteResult]:
    try:
        res = await db.client[DATABASE_NAME][users_collection_name].delete_one({"_id": ObjectId(user_id)})
        if res.deleted_count == 1:
            return USER_DELETED
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def get_user_by_email(user_email: EmailStr) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"email": user_email})
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_hashed_password(user_id: str) -> str:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
        if row:
            return row['hashed_password']
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_all_users():
    try:
        rows = db.client[DATABASE_NAME][users_collection_name].find()
        cursor = await rows.to_list(150)
        for index, user in enumerate(cursor):
            user['_id'] = str(user['_id'])
            cursor[index] = UserResponse(**user)
        return cursor
    except Exception as e:
        raise e