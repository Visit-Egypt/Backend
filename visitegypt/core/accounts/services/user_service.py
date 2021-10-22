from typing import Optional
from visitegypt.core.accounts.entities.user import (
    UserCreate,
    UserResponse,
    User,
    UserUpdate,
    UsersPageResponse,
)
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.errors.user_errors import EmailNotUniqueError, UserNotFoundError
from visitegypt.core.accounts.services.hash_service import get_password_hash
from visitegypt.core.authentication.services.auth_service import (
    login_access_token as login_service,
)
from pydantic import EmailStr
from typing import List


async def register(repo: UserRepo, new_user: UserCreate) -> UserResponse:
    email = new_user.email.lower()
    try:
        user : Optional[UserResponse] = await repo.get_user_by_email(email)
        if user: raise EmailNotUniqueError
    except UserNotFoundError: pass
    except EmailNotUniqueError as email_not_unique: raise email_not_unique
    except Exception as e: raise e

    password_hash = get_password_hash(new_user.password)
    await repo.create_user(User(**new_user.dict(), hashed_password=password_hash))
    token = await login_service(repo, new_user)
    return token


async def get_user_by_id(repo: UserRepo, user_id: str) -> UserResponse:
    try:
        user = await repo.get_user_by_id(user_id)
        if user:
            return user
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def get_all_users(
    repo: UserRepo, page_num: int = 1, limit: int = 15
) -> List[UsersPageResponse]:
    try:
        users = await repo.get_all_users(page_num, limit)
        if users:
            return users
    except Exception as e:
        raise e


async def get_user_by_email(repo: UserRepo, user_email: EmailStr) -> UserResponse:
    try:
        user = await repo.get_user_by_email(user_email)
        if user:
            return user
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def get_user_hashed_password(repo: UserRepo, user_id: str) -> Optional[str]:
    try:
        user_hashed_pass = await repo.get_user_hashed_password(user_id)
        if user_hashed_pass:
            return user_hashed_pass
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def delete_user_by_id(repo: UserRepo, user_id: str) -> Optional[bool]:
    try:
        return await repo.delete_user(user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def update_user_by_id(
    repo: UserRepo, updated_user: UserUpdate, user_id: str
) -> Optional[UserResponse]:
    try:
        return await repo.update_user(updated_user, user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def update_user_role(
    repo: UserRepo, updated_user: str, user_id: str
) -> Optional[UserResponse]:
    try:
        return await repo.update_user_role(updated_user, user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e
