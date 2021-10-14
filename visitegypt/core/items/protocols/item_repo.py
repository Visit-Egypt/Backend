from typing import List, Protocol
from visitegypt.core.items.entities.item import ItemInDB, ItemsPageResponse

class ItemRepo (Protocol):
   async def get_all_items(self, page_num: int, limit: int) -> ItemsPageResponse:
      pass
      
