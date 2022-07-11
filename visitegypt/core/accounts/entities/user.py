from __future__ import annotations
from optparse import Option
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from .roles import Role
from visitegypt.core.base_model import MongoModel, OID
from visitegypt.core.badges.entities.badge import BadgeInDB
from datetime import datetime

class PlaceActivity(MongoModel):
    id: str
    finished: bool
    progress: int

class PlaceActivityUpdate(MongoModel):
    finished: Optional[bool]
    progress: Optional[int]
class BadgeTask(MongoModel):
    badge_id: str
    taskTitle: str
    progress: int
class Badge(MongoModel):
    id: str
    progress: int = 0
    owned: bool = False
    pinned: bool = False

class BadgeUpdate(MongoModel):
    progress: Optional[int]
    owned: Optional[bool]
    pinned: Optional[bool]
class BadgeResponse(MongoModel):
    id: str
    progress: int = 0
    owned: bool = False
    pinned: bool = False
    badge_tasks: List[BadgeTask] = []

class BadgeResponseDetail(MongoModel):
    badge:BadgeInDB = None
    progress: int = 0
    owned: bool = False
    pinned: bool = False
    badge_tasks: List[BadgeTask] = []

class ProfileFrame(MongoModel):
    id: int
    imgUrl: str
    type: int

# User model for Requesting Trip Mate
class RequestTripMate(MongoModel):
    title: str
    description: str

class RequestTripMateInDB(RequestTripMate):
    id: OID = Field()
    initator_id: OID
    is_approved: bool


# Shared properties
class UserBase(MongoModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    photo_link: Optional[str] = None
    bio : Optional[str] = None
    birthdate: Optional[str] = None
    interests: Optional[List[OID]] = []
    followers: Optional[List[OID]] = [] # a list containing followers ids
    following: Optional[List[OID]] = []
    trip_mate_requests: Optional[List[RequestTripMateInDB]] = []
    fav_places: Optional[List[OID]] = []



# Properties to receive via API on creation
class UserCreate(UserBase):
    birthdate: Optional[date] = None
    password: str

class UserCreateToken(UserBase):
    hashed_password: str


# Properties to receive via API on update


class UserUpdaterole(BaseModel):
    user_role: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    photo_link: Optional[str] = None
    xp:Optional[int] = 0
    profileFrame:Optional[ProfileFrame] = None
    postViews:Optional[int] = 0
    bio : Optional[str] = None
    birthdate: Optional[str] = None
    interests: Optional[List[OID]] = None
    followers: Optional[List[OID]] = [] # a list containing followers ids
    following: Optional[List[OID]] = []
    trip_mate_requests: Optional[List[RequestTripMateInDB]] = []
    fav_places: Optional[List[OID]] = []
    device_token: Optional[str] = None
    device_arn_endpoint: Optional[str] = None
    ar_obj:Optional[str] = None
    ar_png:Optional[str] = None
    ar_mtl:Optional[str] = None

class UserUpdatePassword(BaseModel):
    hashed_password: str
class UserInDBBase(UserBase):
    # id: str = Field(..., alias='_id')
    id: OID = Field()
    user_role: str = Role.USER.get("name")
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserPushNotification(UserInDBBase):
    device_token: str = ''
    device_arn_endpoint: str = ''

# Additional properties to return via API
class User(UserBase):
    hashed_password: str
    user_role: Optional[str] = Role.USER.get("name")
    xp:Optional[int] = 0
    badges:Optional[List[Badge]] = []
    badge_tasks: Optional[List[BadgeTask]] = []
    placeActivities: Optional[List[PlaceActivity]] = []
    profileFrame:Optional[ProfileFrame] = None
    postViews:Optional[List[str]] = []


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
    


class UserResponse(UserInDBBase):
    xp:Optional[int] = 0
    badges:Optional[List[Badge]] = []
    badge_tasks: Optional[List[BadgeTask]] = []
    placeActivities: Optional[List[PlaceActivity]] = []
    profileFrame:Optional[ProfileFrame] = None
    postViews:Optional[List[str]] = []
    ar_obj:Optional[str] = None
    ar_png:Optional[str] = None
    ar_mtl:Optional[str] = None

class UserAR(BaseModel):
    ar_obj:str
    ar_png:str
    ar_mtl:str

class UserResponseInTags(MongoModel):
    id: OID = Field()
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_link: Optional[str] = None
    device_arn_endpoint: Optional[str]



class UsersPageResponse(MongoModel):
    current_page: int
    content_range: int
    has_next: bool
    users: Optional[List[UserResponse]]



class UserPrefsReq(BaseModel):
    pref_list: List[str]

class UserFollowResp(BaseModel):
    followers_num : str