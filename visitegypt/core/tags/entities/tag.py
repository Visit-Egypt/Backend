from optparse import Option
from pydantic import BaseModel, Field
from visitegypt.core.base_model import MongoModel, OID
from typing import List, Optional

class Tag(MongoModel):
    id: OID = Field()
    name: str
    description: Optional[str] = ''

class TageInDB(Tag):
    users: Optional[List[OID]] = []
    posts: Optional[List[OID]] = []

class TagCreation(BaseModel):
    name: str
    description: Optional[str] = ''

class TagUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    users: Optional[List[OID]]
    posts: Optional[List[OID]]

class UsersTagsReq(BaseModel):
    tags_ids: List[str]