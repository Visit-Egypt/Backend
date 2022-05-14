from typing import List, Optional
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID

class BadgeTask(MongoModel):
    imgUrl: str
    taskTitle: str
    max_progress: int


class BadgeBase(MongoModel):
    img_url: str
    place_id: str
    city: str
    max_progress: int
    title: str
    type: str
    xp: int
    description: str
    badge_tasks: List[BadgeTask]

class BadgeInDB(BadgeBase):
    id: OID = Field()

class BadgesPageResponse(MongoModel):
    current_page: int
    content_range: int
    has_next: bool
    badges: Optional[List[BadgeInDB]]

class BadgeUpdate(MongoModel):
    img_url: Optional[str]
    place_id: Optional[str]
    max_progress: Optional[int]
    title: Optional[str]
    type: Optional[str]
    xp: Optional[int]
    description: Optional[str]
    badge_tasks: Optional[List[BadgeTask]]