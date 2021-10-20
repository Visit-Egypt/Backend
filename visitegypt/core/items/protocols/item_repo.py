from typing import Dict, Protocol
from visitegypt.core.items.entities.item import (
    ItemInDB,
    ItemsPageResponse,
    ItemBase,
    ItemUpdate,
)


class ItemRepo(Protocol):
    async def get_filtered_items(
        self, page_num: int, limit: int, filters: Dict
    ) -> ItemsPageResponse:
        pass

    async def create_item(self, item_to_create: ItemBase) -> ItemInDB:
        pass

    async def update_item(item_to_update: ItemUpdate, item_id: str) -> ItemInDB:
        pass

    async def delete_item(self, item_id: str) -> bool:
        pass
