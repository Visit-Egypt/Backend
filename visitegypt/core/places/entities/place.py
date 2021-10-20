from typing import List, Optional
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID


class review(MongoModel):
    rating: float
    review: Optional[str]
    user_id: str
    user_name: str


class CreatePlace(MongoModel):
    title: str
    description: str
    locationDescription: Optional[str] = None
    longitude: Optional[int] = None
    altitude: Optional[int] = None
    imageUrls: Optional[List[str]] = []
    default_image: Optional[str] = None


class PlaceBase(CreatePlace):
    reviews: Optional[List[review]] = []


class UpdatePlace(MongoModel):
    title: Optional[str] = None
    description: Optional[str] = None
    locationDescription: Optional[str] = None
    longitude: Optional[int] = None
    altitude: Optional[int] = None
    imageUrls: Optional[List[str]] = None
    default_image: Optional[str] = None


class PlaceInDB(PlaceBase):
    id: OID = Field()


class PlacesPageResponse(MongoModel):
    current_page: int
    has_next: bool
    places: Optional[List[PlaceInDB]]
