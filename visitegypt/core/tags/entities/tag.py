from pydantic import BaseModel, Field
from visitegypt.core.base_model import MongoModel, OID
from typing import List, Optional
from datetime import datetime

class Tag(MongoModel):
    id: OID = Field()
    name: str
    description: Optional[str] = ''
    users: Optional[List[OID]] = []
    posts: Optional[List[OID]] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
class TagCreation(BaseModel):
    name: str
    description: Optional[str] = ''

class TagUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    users: Optional[List[OID]]
    posts: Optional[List[OID]]
    topic_arn: Optional[str]

class UsersTagsReq(BaseModel):
    tags_ids: List[str]

class GetTagResponse(MongoModel):
    id: OID = Field()
    name: str
    description: Optional[str] = ''