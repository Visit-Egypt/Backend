from optparse import Option
from visitegypt.core.tags.entities.tag import Tag, TagUpdate, TagCreation
from visitegypt.core.tags.protocols.tag_repo import TagRepo
from typing import Dict, List, Optional
from visitegypt.core.errors.tag_error import TagsNotFound, TagAlreadyExists, TagCreationError

async def get_all_tags(repo: TagRepo, filters: Dict) -> Optional[List[Tag]]:
    try:
        tags_list = await repo.get_all_tags(filters)
        if tags_list:
            return tags_list
            
    except TagsNotFound as tagnot: raise tagnot
    except Exception as e: raise e


async def add_new_tag(repo: TagRepo, new_tag: TagCreation) -> Optional[Tag]:
    try:
        # Add the tag to the db
        return await repo.add_tag(new_tag)
    except TagAlreadyExists as tae: raise tae
    except TagCreationError as tcr: raise tcr
    except Exception as e: raise e
