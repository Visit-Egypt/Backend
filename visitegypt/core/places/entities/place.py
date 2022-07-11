from email import message
from locale import currency
from optparse import Option
from pydoc import describe
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
from visitegypt.core.base_model import MongoModel, OID, Translatable
from datetime import datetime




class TicketValue(BaseModel):
    currency: str
    price: str

class Ticket(BaseModel):
    description: str
    value: TicketValue

class TranslatebleAttributes(BaseModel):
    title: str
    long_description: Optional[str]
    short_description: Optional[str]
    location_description: Optional[str]
    city: Optional[str]
    ticket_prices: Optional[List[Ticket]]

class Hint(MongoModel):
    hint: str
    imageUrl: str
class Explore(MongoModel):
    id: str
    xp: int
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
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class review(MongoModel):
    rating: float
    review: Optional[str]
    user_id: str
    user_name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

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
    category: List[str] = []
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
    category: List[str] = []
    city: Optional[str]
    views: Optional[int] = 0
    explores: Optional[List[Explore]]
    placeActivities: Optional[List[PlaceActivity]]

class PlaceInDB(PlaceWithReviews):
    id: OID = Field()
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

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




"""
class NewPlaceModel(MongoModel):
    id: OID = Field()
    translations: Dict[str, TranslatebleAttributes]
"""