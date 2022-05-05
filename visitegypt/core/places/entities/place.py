from tracemalloc import start
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
from visitegypt.core.base_model import MongoModel, OID
from visitegypt.core.tags.entities.tag import Tag

class Hint(MongoModel):
    hint: str
    imageUrl: str
class Explore(MongoModel):
    id: str
    title: str
    imageUrl: str
    hints: List[Hint]

class PlaceActivity(MongoModel):
    id: str
    xp: int
    customXp: bool
    type: int
    title: str
    description: str
    duration:str
    maxProgress: int

class review(MongoModel):
    rating: float
    review: Optional[str]
    user_id: str
    user_name: str

class PlaceBase(MongoModel):
    title: str
    long_description: Optional[str]
    short_description: Optional[str]
    location_description: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    image_urls: Optional[List[str]]
    default_image: Optional[str]
    opening_hours: Optional[str]
    city: Optional[str]
    ticket_prices: Optional[Dict[Any, Any]]
    category: List[Tag] = []
    views: Optional[int] = 0
    explores: Optional[List[Explore]]
    placeActivities: Optional[List[PlaceActivity]]


class PlaceWithReviews(PlaceBase):
    reviews: Optional[List[review]] = []



class UpdatePlace(MongoModel):
    title: Optional[str]
    description: Optional[str]
    location_description: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    image_urls: Optional[List[str]]
    default_image: Optional[str]
    opening_hours: Optional[str]
    category: List[Tag] = []
    city: Optional[str]
    views: Optional[int] = 0
    explores: Optional[List[Explore]]
    placeActivities: Optional[List[PlaceActivity]]

class PlaceInDB(PlaceWithReviews):
    id: OID = Field()


class PlacesPageResponse(MongoModel):
    current_page: int
    has_next: bool
    places: Optional[List[PlaceInDB]]


class TicketModel(MongoModel):
    pass

class PlaceForSearch(MongoModel):
    id: OID = Field()
    title: str
    default_image: Optional[str]

class OpeningHoursPeriods(BaseModel):
    pass

class OpeningHours(BaseModel):
    day : str = ''
    periods: bool
