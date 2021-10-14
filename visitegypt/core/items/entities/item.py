from typing import List, Optional
from pydantic import Field
from visitegypt.core.base_model import *


class ItemBase(MongoModel):
    title: str
    short_description: str
    long_description: Optional[str]
    default_image: Optional[str]
    list_of_images: Optional[List[str]]


class ItemInDB(ItemBase):
    id: OID = Field()


class ItemsPageResponse(MongoModel):
    current_page: int
    has_next: bool
    items: Optional[List[ItemInDB]]