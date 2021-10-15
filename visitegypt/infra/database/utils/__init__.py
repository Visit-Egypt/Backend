from typing import Dict, List, Tuple


users_collection_name = "Users"
items_collection_name = "Items"
places_collection_name = "Places"


def calculate_start_index(page_size, page_num) -> Tuple[int, int]:
    """returns a set of documents belonging to page number `page_num`
    where size of each page is `page_size`.
    """
    # Calculate number of documents to skip
    start_index = page_size * (page_num - 1)
    end_index = page_size * page_num
   
    # Skip and limit
    # cursor = db['students'].find().skip(skips).limit(page_size)

    # Return skips
    return (start_index, end_index)

async def check_has_next(start_index: int, db_session) -> bool:
        docs_count = await db_session.count_documents({})
        return not (docs_count - 1 <= start_index)
