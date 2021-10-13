from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId, InvalidId

from pydantic import BaseModel, EmailStr, Field, BaseConfig
from .roles import Role


class OID(str):
  @classmethod
  def __get_validators__(cls):
      yield cls.validate

  @classmethod
  def validate(cls, v):
      try:
          return ObjectId(str(v))
      except InvalidId:
          raise ValueError("Not a valid ObjectId")

class MongoModel(BaseModel):

  class Config(BaseConfig):
      allow_population_by_field_name = True
      json_encoders = {
          datetime: lambda dt: dt.isoformat(),
          ObjectId: lambda oid: str(oid),
      }

  @classmethod
  def from_mongo(cls, data: dict):
      """We must convert _id into "id". """
      if not data:
          return data
      id = data.pop('_id', None)
      return cls(**dict(data, id=id))

  def mongo(self, **kwargs):
      exclude_unset = kwargs.pop('exclude_unset', True)
      by_alias = kwargs.pop('by_alias', True)

      parsed = self.dict(
          exclude_unset=exclude_unset,
          by_alias=by_alias,
          **kwargs,
      )

      # Mongo uses `_id` as default key. We should stick to that as well.
      if '_id' not in parsed and 'id' in parsed:
          parsed['_id'] = parsed.pop('id')

      return parsed


# Shared properties
class UserBase(MongoModel):
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
    # id: str = Field(..., alias='_id') 
    id: OID = Field()
    user_role: str = Role.USER.get('name')
    # created_at: datetime
    # updated_at: datetime


# Additional properties to return via API
class User(UserBase):
    hashed_password: str
    user_role: Optional[str] = Role.USER.get('name')


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

class UserResponse(UserInDBBase):
    pass
class UsersResponse(UserBase):
    user_role: str = Role.USER.get('name')
