from typing import Optional
from visitegypt.core.accounts.entities.user import (
    UserCreate,
    UserResponse,
    User,
    UserUpdate,
    UserUpdatePassword,
    UsersPageResponse,
    Badge,
    BadgeTask,BadgeUpdate,PlaceActivity,PlaceActivityUpdate
    , RequestTripMate,
    UserInDB,
    UserCreateToken,
    UserFollowResp
)
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.errors.user_errors import EmailNotUniqueError, UserNotFoundError, TripRequestNotFound, UserIsFollower, UserIsNotFollowed
from visitegypt.core.errors.tag_error import TagsNotFound
from visitegypt.core.accounts.services.hash_service import get_password_hash
from visitegypt.core.authentication.entities.userauth import UserGoogleAuthBody
from visitegypt.core.authentication.services.auth_service import (
    login_access_token as login_service,
)
from visitegypt.core.authentication.services.auth_service import register_access_token,forgot_password_token
from visitegypt.core.authentication.services.auth_service import login_google_access_token
from pydantic import EmailStr
from typing import List
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid
from visitegypt.api.utils import get_register_user,send_mail,get_reset_password_user,send__reset_password_mail
from visitegypt.resources.strings import MESSAGE_404
from datetime import datetime
from visitegypt.config.environment import CLIENT_ID

API_HOST = "https://visit-egypt.herokuapp.com"

async def new_register(repo: UserRepo, new_user: UserCreate) -> UserResponse:
    new_user = new_user.dict()
    if(new_user["birthdate"]):
        new_user["birthdate"] = datetime.strftime(new_user["birthdate"],"%y-%m-%d")
    email = new_user["email"].lower()
    try:
        user : Optional[UserResponse] = await repo.get_user_by_email(email)
        if user: raise EmailNotUniqueError
    except UserNotFoundError: pass
    except EmailNotUniqueError as email_not_unique: raise email_not_unique
    except Exception as e: raise e

    password_hash = get_password_hash(new_user["password"])
    user = UserCreateToken(**new_user, hashed_password=password_hash).dict()
    token = register_access_token(repo, user)
    url = API_HOST+"/api/user/verfiy/"+str(token)
    await send_mail(email=email,url=url)
    return "Verfication email is sent, please verify your email"

async def forgot_password(repo:UserRepo,email:str):
    email = email.lower()
    try:
        user : Optional[UserResponse] = await repo.get_user_by_email(email)
        token = await forgot_password_token(repo,user)
        url = API_HOST+"/api/user/resetpassword/"+str(user.id)+"/"+str(token)
        await send__reset_password_mail(url,email)
        return "Reset Password email is sent please check your email"
    except UserNotFoundError: HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as e: raise e

async def check_user_id(repo:UserRepo, user_id:str ,token:str):
    try:
        user_hash = await repo.get_user_hashed_password(user_id)
        payload = get_reset_password_user(user_hash,token=token)
        if user_id != payload["id"]:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e: raise e

async def reset_password(repo: UserRepo,user_id:str ,token:str ,new_password: str):
    try:
        user_hash = await repo.get_user_hashed_password(user_id)
        payload = get_reset_password_user(user_hash,token=token)
        password_hash = get_password_hash(new_password)
        await repo.update_user_password(UserUpdatePassword(**{"hashed_password":password_hash}),payload["id"])
        return "Password Successfully Reseted"
    except Exception as e: raise e

async def create_user(repo: UserRepo, token: str):
    try:
        user = get_register_user(token=token)
        try:
            user : Optional[UserResponse] = await repo.get_user_by_email(user["email"].lower())
            if user: raise EmailNotUniqueError
        except UserNotFoundError: pass
        except EmailNotUniqueError as email_not_unique: raise email_not_unique
        except Exception as e: raise e
        await repo.create_user(User(**user))
        return "Account Successfully Created"
    except Exception as e: raise e

async def google_register(repo: UserRepo, token: UserGoogleAuthBody) -> UserResponse:
    try:
        user = id_token.verify_oauth2_token(token.token, requests.Request(), CLIENT_ID)
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    email = user["email"]
    try:
        user : Optional[UserResponse] = await repo.get_user_by_email(email)
        if user: raise EmailNotUniqueError
    except UserNotFoundError: pass
    except EmailNotUniqueError as email_not_unique: raise email_not_unique
    except Exception as e: raise e

    password = str(uuid.uuid1())
    password_hash = get_password_hash(password)
    new_user = {
        "email":user["email"],
        "first_name":user["given_name"],
        "last_name":user["family_name"],
        "photo_link":user["picture"],
        "hashed_password":password_hash
    }
    await repo.create_user(User(**new_user))
    newtoken = await login_google_access_token(repo,token)
    return newtoken

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

async def update_badge_task(repo: UserRepo, user_id: str ,new_task: BadgeTask):
    try:
        
        user_badges = await repo.update_badge_task(user_id, new_task)
        if user_badges:
            return user_badges
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def update_badge(repo: UserRepo, user_id: str ,badge_id: str,new_badge: BadgeUpdate):
    try:
        user_badges = await repo.update_badge(user_id,badge_id, new_badge)
        if user_badges:
            return user_badges
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_badges(repo: UserRepo, user_id: str):
    try:
        user_badges = await repo.get_user_badges(user_id)
        if user_badges:
            return user_badges
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def update_place_activity(repo: UserRepo, user_id: str, activity_id: str, new_activity:PlaceActivityUpdate):
    try:
        user_activities = await repo.update_user_activity(user_id,activity_id,new_activity)
        if user_activities:
            return user_activities
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_activities(repo: UserRepo, user_id: str):
    try:
        user_activities = await repo.get_user_activities(user_id)
        if user_activities:
            return user_activities
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def follow_user(repo: UserRepo, current_user: UserResponse, user_id: str) -> UserFollowResp:
    try:
        user_followed = await repo.follow_user(current_user, user_id)
        if user_followed:
            return user_followed
    except UserIsFollower as usf: raise usf
    except UserNotFoundError as ue: raise ue
    except Exception as e: raise e

async def unfollow_user(repo: UserRepo, current_user: UserResponse, user_id: str) -> UserFollowResp:
    try:
        user_followed = await repo.unfollow_user(current_user, user_id)
        if user_followed:
            return user_followed
    except UserIsNotFollowed as uu: raise uu
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def request_trip_mate(repo: UserRepo, current_user: UserResponse, user_id: str, request_mate: RequestTripMate) -> bool:
    try:
        added = await repo.request_trip_mate(current_user, user_id, request_mate)
        if added:
            return added
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def approve_request_trip_mate(repo: UserRepo, current_user: UserResponse, req_id: str) -> Optional[UserResponse]:
    try:
        return await repo.approve_request_trip_mate(current_user, req_id)
    except UserNotFoundError as un: raise un
    except TripRequestNotFound as trf: raise trf
    except Exception as e: raise e

async def add_preferences(repo: UserRepo, current_user: UserResponse, list_of_prefs: List[str]) -> Optional[UserResponse]:
    try:
        return await repo.add_preferences(current_user, list_of_prefs)
    except UserNotFoundError as un: raise un
    except Exception as e: raise e


async def remove_preferences(repo: UserRepo, current_user: UserResponse, list_of_prefs: List[str]) -> Optional[UserResponse]:
    try:
        return await repo.remove_preferences(current_user, list_of_prefs)
    except UserNotFoundError as un: raise un
    except TagsNotFound as ue: raise ue
    except Exception as e: raise e
