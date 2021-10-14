from typing import List
from visitegypt.core.errors.item_error import ItemNotFoundError
from visitegypt.core.items.entities.item import ItemInDB, ItemsPageResponse
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import items_collection_name
from visitegypt.infra.database.utils import calculate_start_index, check_has_next
from pydantic import parse_obj_as

async def get_all_items(page_num: int, limit: int) -> ItemsPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index : int = indcies[0]
        cursor = db.client[DATABASE_NAME][items_collection_name].find().skip(start_index).limit(limit)
        items_list = await cursor.to_list(limit)
        if not items_list: raise ItemNotFoundError
        items_list_response = [ItemInDB.from_mongo(item) for item in items_list]
        has_next = await check_has_next(start_index, db.client[DATABASE_NAME][items_collection_name])
        return ItemsPageResponse(current_page=page_num, has_next=has_next, items = items_list_response)
    except Exception as e:
        raise e 