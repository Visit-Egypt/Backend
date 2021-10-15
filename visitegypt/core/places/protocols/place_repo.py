from typing import List, Protocol
from visitegypt.core.places.entities.place import PlaceInDB, PlacesPageResponse, PlaceBase, UpdatePlace, review
from typing import List, Optional

class PlaceRepo (Protocol):
   async def get_all_places(self, page_num: int, limit: int) -> PlacesPageResponse:
      pass
   async def get_place_by_id(place_id: str) -> Optional[PlaceInDB]:
      pass
   async def get_place_by_title(place_title: str) -> Optional[PlaceInDB]:
      pass
   async def create_place(new_place: PlaceBase) -> PlaceInDB:
      pass
   async def delete_place(place_id: str):
      pass
   async def update_place(updated_place:UpdatePlace,place_id:str) -> Optional[PlaceInDB] :
      pass
   async def add_review(place_id:str, new_reviw:review):
      pass
   async def delete_review(place_id:str, review:review):
      pass