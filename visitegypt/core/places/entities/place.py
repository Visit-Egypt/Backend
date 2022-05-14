from email import message
from typing import Any, List, Optional, Dict
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID


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
    category: Optional[str]
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
    city: Optional[str]
    views: Optional[int] = 0
    explores: Optional[List[Explore]]
    placeActivities: Optional[List[PlaceActivity]]

class PlaceInDB(PlaceWithReviews):
    id: OID = Field()


class PlacesPageResponse(MongoModel):
    current_page: int
    content_range: int
    has_next: bool
    places: Optional[List[PlaceInDB]]


class TicketModel(MongoModel):
    pass

class PlaceForSearch(MongoModel):
    id: OID = Field()
    title: str
    default_image: Optional[str]
