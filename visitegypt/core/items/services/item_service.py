from visitegypt.core.items.entities.item import ItemsPageResponse
from visitegypt.core.items.protocols.item_repo import ItemRepo
from visitegypt.core.errors.item_error import *

async def get_all_items_paged(repo: ItemRepo, page_num: int = 1, limit: int = 15) -> ItemsPageResponse:
    try:
        items  = await repo.get_all_items(page_num, limit)
        if items: 
            return items
        raise ItemNotFoundError
    except ItemNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e
