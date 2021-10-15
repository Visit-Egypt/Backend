from typing import Dict, Optional
from visitegypt.core.items.entities.item import ItemBase, ItemInDB, ItemsPageResponse, ItemUpdate
from visitegypt.core.items.protocols.item_repo import ItemRepo
from visitegypt.core.errors.item_error import *

async def get_filtered_items(repo: ItemRepo, page_num: int = 1, limit: int = 15, filters: Dict = None) -> ItemsPageResponse:
    try:
        items  = await repo.get_filtered_items(page_num=page_num, limit=limit, filters=filters)
        if items: 
            return items
        raise ItemNotFoundError
    except ItemNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e


async def create_item(repo: ItemRepo, item_to_create: ItemBase) -> ItemInDB:
    try:
        c_i = await get_filtered_items(repo, page_num=1,limit=1,filters={"title":item_to_create.title})
        if c_i.items[0]: raise ItemAlreadyExists
    except ItemAlreadyExists as iee: raise iee
    except ItemNotFoundError: pass
    except Exception as e: raise e
    
    try:
        return await repo.create_item(item_to_create)
    except Exception as e:
        raise e


async def delete_item_by_id(repo: ItemRepo, item_id: str) -> bool:
    try:
        return await repo.delete_item(item_id)
    except ItemNotFoundError as ue:
            raise ue
    except Exception as e:
        raise e

async def update_item_by_id(repo: ItemRepo,item_to_update:ItemUpdate, item_id: str) -> Optional[ItemInDB]:
    try:
        return await repo.update_item(item_id=item_id, item_to_update=item_to_update)
    except ItemNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e