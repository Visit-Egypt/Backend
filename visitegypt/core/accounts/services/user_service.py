from typing import Optional
from visitegypt.core.accounts.entities.user import UserCreate, UserResponse, User
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.accounts.services.exceptions import EmailNotUniqueError, UserNotFoundError
from visitegypt.core.accounts.services.hash_service import get_password_hash


async def register(repo: UserRepo, new_user: UserCreate) -> UserResponse:
    email = new_user.email.lower()
    try:
        user = await repo.get_user_by_email(email)
        print(user)
        if user: raise EmailNotUniqueError
    except Exception as e:
        raise e
 
    password_hash = get_password_hash(new_user.password)
    user = await repo.create_user(User(**new_user.dict(), hashed_password= password_hash))
    return user

async def get_user_by_id(repo: UserRepo, user_id: str) -> UserResponse:
    user  = await repo.get_user_by_id(user_id)
    if user: return user
    raise UserNotFoundError

async def get_user_by_email(repo: UserRepo, user_email: str) -> UserResponse:
    user = await repo.get_user_by_email(user_email)
    if user: return user
    raise UserNotFoundError

async def get_user_hashed_password(repo: UserRepo, user_id: str) -> Optional[str]:
    user_hashed_pass = await repo.get_user_hashed_password(user_id)
    if user_hashed_pass: return user_hashed_pass
    raise UserNotFoundError