from typing import Protocol, Optional, List, Dict
from visitegypt.core.places.entities.place import (
    PlaceInDB,
    PlacesPageResponse,
    PlaceBase,
    UpdatePlace,
    review,
    PlaceForSearch
)


class PlaceRepo(Protocol):
    async def get_filtered_places(self, page_num: int, limit: int, filters: Dict) -> PlacesPageResponse:
        pass
    async def get_all_places(self, page_num: int, limit: int, filters: Dict) -> PlacesPageResponse:
        pass

    async def get_all_city_places(city_name: str,page_num: int, limit: int) -> PlacesPageResponse:
        pass

    async def get_place_by_id(place_id: str) -> Optional[PlaceInDB]:
        pass

    async def get_place_by_title(place_title: str) -> Optional[PlaceInDB]:
        pass

    async def create_place(new_place: PlaceBase) -> PlaceInDB:
        pass

    async def delete_place(place_id: str):
        pass

    async def update_place(
        updated_place: UpdatePlace, place_id: str
    ) -> Optional[PlaceInDB]:
        pass

    async def add_review(place_id: str, new_reviw: review):
        pass

    async def delete_review(place_id: str, review: review):
        pass

    async def search_place(search_text:str) -> Optional[List[PlaceForSearch]]:
        pass

    async def get_cities():
        pass

    async def get_some_places(places_ids:List) -> List[PlaceInDB]:
        pass
