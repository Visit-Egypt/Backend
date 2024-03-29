from typing import List, Tuple, Dict


users_collection_name = "Users"
items_collection_name = "Items"
places_collection_name = "Places"
posts_collection_name = "Posts"
hotels_collection_name= "Hotels"
kings_collection_name = "Kings"
restaurants_collection_name = "Restaurants"
pharmacies_collection_name = "Pharmacies"
badges_collection_name = "Badges"
tags_collection_name = "Tags"
notifications_collection_name = "Notifications"
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


def check_has_next(start_index: int, document_count: int) -> bool:
    return not (document_count - 1 <= start_index)

def check_next(limit:int,items:List):
    return not(len(items)<limit)