from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId

from pydantic import BaseModel, EmailStr, Field
from .roles import Role




# Shared properties
class UserBase(BaseModel):
    email:EmailStr
    first_name: Optional[str] = None
    last_name : Optional[str] = None
    phone_number: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# Properties to receive via API on update

class UserUpdaterole(BaseModel):
    user_role : str
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name : Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    




class UserInDBBase(UserBase):
    id: str = Field(..., alias='_id') 
    user_role: str = Role.GUEST.get('name')
    #created_at: datetime
   # updated_at: datetime


# Additional properties to return via API
class User(UserBase):
    hashed_password: str


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
    user_role: Optional[str]

class UserResponse(UserInDBBase):
    pass

