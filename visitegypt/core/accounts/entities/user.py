from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from .roles import Role
from visitegypt.core.base_model import MongoModel, OID


class Badge(MongoModel):
    id: int
    imgUrl: str
    type: int

class ProfileFrame(MongoModel):
    id: int
    imgUrl: str
    type: int

# Shared properties
class UserBase(MongoModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    photo_link: Optional[str] = None



# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update


class UserUpdaterole(BaseModel):
    user_role: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    photo_link: Optional[str] = None
    xp:Optional[int] = 0
    badges:Optional[List[Badge]] = []
    profileFrame:Optional[ProfileFrame] = None
    postسViews:Optional[int] = 0


class UserInDBBase(UserBase):
    # id: str = Field(..., alias='_id')
    id: OID = Field()
    user_role: str = Role.USER.get("name")
    # created_at: datetime
    # updated_at: datetime


# Additional properties to return via API
class User(UserBase):
    hashed_password: str
    user_role: Optional[str] = Role.USER.get("name")
    xp:Optional[int] = 0
    badges:Optional[List[Badge]] = []
    profileFrame:Optional[ProfileFrame] = None
    postViews:Optional[List[str]] = []


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
    


class UserResponse(UserInDBBase):
    pass


class UsersPageResponse(MongoModel):
    current_page: int
    has_next: bool
    users: Optional[List[UserResponse]]
