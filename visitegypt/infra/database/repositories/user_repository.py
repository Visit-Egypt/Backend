from typing import Optional
from pydantic import EmailStr
from visitegypt.core.accounts.entities.user import UserResponse, UserInDB, UserUpdate, User

from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import users_collection_name

from bson import ObjectId

async def create_user(new_user: User) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].insert_one(new_user.dict())
        dbuser = UserResponse(**new_user.dict())
        dbuser.id = str(row.inserted_id)
        return dbuser
    except Exception as e:
        raise e

async def update_user(updated_user: UserUpdate) -> Optional[UserInDB]: 
    pass

async def delete_user(user_id: str) -> Optional[str]:
    pass

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