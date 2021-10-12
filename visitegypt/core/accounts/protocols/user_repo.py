from typing import Protocol, Optional
from typing import List
from pydantic import EmailStr
from visitegypt.core.accounts.entities.user import UserResponse, UserUpdate, User,UserUpdaterole,UsersResponse
from pymongo.results import DeleteResult

class UserRepo (Protocol):
    async def create_user(self, new_user: User) -> Optional[UserResponse]:
        pass

    async def update_user(self, updated_user: UserUpdate,user_id:str): 
        pass

    async def delete_user(self, user_id: str) -> Optional[DeleteResult]:
        pass

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        pass

    async def get_user_by_email(self, user_email: EmailStr) -> Optional[UserResponse]:
        pass
    async def get_user_hashed_password(user_id: str) -> str:
        pass
    async def update_user_role(updated_user: UserUpdaterole,user_id:str):
        pass
    async def get_all_users():
        pass