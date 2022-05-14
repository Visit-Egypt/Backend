from typing import List, Optional
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID

class PostBase(MongoModel):
    caption: str
    list_of_images: Optional[List[str]]
    place_id: str
    user_id: str
    user_name: str
    likes: Optional[List[str]]

class PostInDB(PostBase):
    id: OID = Field()

class UpdatePost(MongoModel):
    caption: Optional[str]
    list_of_images: Optional[List[str]]

class PostsPageResponse(MongoModel):
    current_page: int
    content_range: int
    has_next: bool
    posts: Optional[List[PostInDB]]

