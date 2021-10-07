from typing import Optional
from pydantic import EmailStr
from visitegypt.core.accounts.entities.user import UserResponse, UserInDB, UserUpdate, User
from visitegypt.core.accounts.services.hash_service import get_password_hash
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import users_collection_name
from pymongo.results import DeleteResult


from bson import ObjectId

async def create_user(new_user: User) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].insert_one(new_user.dict())
        if row.inserted_id:
            return await get_user_by_id(row.inserted_id)
    except Exception as e:
        raise e

async def update_user(updated_user: UserUpdate,user_id:str) : 
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
        if updated_user.user_role:
            result = await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"user_role": updated_user.user_role}})
        return "User updated"
    except Exception as e:
        raise e

async def delete_user(user_id: str) -> Optional[DeleteResult]:
    try:
        await db.client[DATABASE_NAME][users_collection_name].delete_one({"_id": ObjectId(user_id)})
    except Exception as e:
        raise e

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
        if row:
            row['_id'] = str(row['_id'])
            return UserResponse(**row)
        return None
    except Exception as e:
        raise e


async def get_user_by_email(user_email: EmailStr) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"email": user_email})
        if row:
            row['_id'] = str(row['_id'])
            return UserResponse(**row)
        return None
    except Exception as e:
        raise e

async def get_user_hashed_password(user_id: str) -> str:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one({"_id": ObjectId(user_id)})
        if row:
            return row['hashed_password']
        return None
    except Exception as e:
        raise e