from typing import Protocol, Optional, List

from pydantic import EmailStr
from visitegypt.core.accounts.entities.user import (
    UserResponse,
    UserUpdate,
    User,
    UserUpdaterole,
    Badge,
    BadgeTask,
    BadgeUpdate,
    PlaceActivity,
    PlaceActivityUpdate,
    RequestTripMate
)


class UserRepo(Protocol):
    async def create_user(self, new_user: User) -> Optional[UserResponse]:
        pass

    async def update_user(
        self, updated_user: UserUpdate, user_id: str
    ) -> Optional[UserResponse]:
        pass

    async def delete_user(self, user_id: str) ->  Optional[bool]:
        pass

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        pass

    async def get_user_by_email(self, user_email: EmailStr) -> Optional[UserResponse]:
        pass

    async def get_user_hashed_password(user_id: str) -> str:
        pass

    async def update_user_role(
        updated_user: UserUpdaterole, user_id: str
    ) -> Optional[UserResponse]:
        pass

    async def get_all_users(page_num: int, limit: int):
        pass
    async def update_user_tokenID(user_id: str,new_toke_id:str,old_token_id:str=None):
        pass
    async def check_user_token(user_id: str,token_id:str) -> UserResponse:
        pass
    async def user_logout(user_id: str):
        pass
    async def update_badge_task(user_id:str, new_task:BadgeTask):
        pass
    async def update_badge(user_id: str ,badge_id: str,new_badge: BadgeUpdate):
        pass
    async def get_user_badges( user_id: str):
        pass
    async def update_user_activity(user_id:str,activity_id:str,new_activity:PlaceActivityUpdate):
        pass
    async def get_user_activities( user_id: str):
        pass

    async def follow_user(current_user: UserResponse, user_id: str) -> bool:
        pass
    async def unfollow_user(current_user: UserResponse, user_id: str) -> bool:
        pass
    async def request_trip_mate(self, current_user: UserResponse, user_id: str, request_mate: RequestTripMate) -> Optional[UserResponse]:
        pass
    async def approve_request_trip_mate(self, current_user: UserResponse, req_id: str) -> Optional[UserResponse]:
        pass
    
    async def add_preferences(self, current_user: UserResponse, list_of_prefs: List[str]) -> Optional[UserResponse]:
        pass
    
    async def remove_preferences(self, current_user: UserResponse, list_of_remv_prefs: List[str]) -> Optional[UserResponse]:
        pass

    async def add_place_to_favs(self, current_user: UserResponse, place_id: str) -> Optional[bool]:
        pass

    async def remove_place_from_favs(self,current_user: UserResponse, place_id: str) -> Optional[bool]:
        pass
    