from typing import Protocol, Optional

from pydantic import EmailStr
from visitegypt.core.accounts.entities.user import UserResponse, UserUpdate, User

class UserRepo (Protocol):
    async def create_user(self, new_user: User) -> Optional[UserResponse]:
        pass

    async def update_user(self, updated_user: UserUpdate) -> Optional[UserResponse]: 
        pass

    async def delete_user(self, user_id: str) -> Optional[str]:
        pass

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        pass

    async def get_user_by_email(self, user_email: EmailStr) -> Optional[UserResponse]:
        pass
    async def get_user_hashed_password(user_id: str) -> str:
        pass