from typing import List, Optional
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID
from datetime import datetime

class ItemBase(MongoModel):
    title: str
    short_description: str
    long_description: Optional[str]
    default_image: Optional[str]
    list_of_images: Optional[List[str]]
    place_id: Optional[str]


class ItemInDB(ItemBase):
    id: OID = Field()
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
class ItemsPageResponse(MongoModel):
    current_page: int
    content_range: int
    has_next: bool
    items: Optional[List[ItemInDB]]


class ItemUpdate(MongoModel):
    title: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    default_image: Optional[str]
    list_of_images: Optional[List[str]]
    place_id: Optional[str]
