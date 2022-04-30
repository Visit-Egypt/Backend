from optparse import Option
from visitegypt.core.tags.entities.tag import Tag, TagUpdate, TagCreation
from visitegypt.core.tags.protocols.tag_repo import TagRepo
from typing import Dict, List, Optional
from visitegypt.core.errors.tag_error import TagsNotFound, TagAlreadyExists, TagCreationError
from visitegypt.core.accounts.entities.user import UserResponse
from bson import ObjectId
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

async def update_tag(repo: TagRepo, update_tag: TagUpdate, tag_id: str) -> Optional[Tag]:
    try:
        return await repo.update_tag(update_tag, tag_id)
    except TagsNotFound as tnf: raise tnf
    except Exception as e: raise e

async def delete_tag(repo: TagRepo, tag_id: str) -> Optional[bool]:
    try:
        return await repo.delete_tag(tag_id)
    except TagsNotFound as tnf: raise tnf
    except Exception as e: raise e

async def get_all_users_of_tags(repo: TagRepo, tag_ids: List[str])-> Optional[List[UserResponse]]:
    try:
        return await repo.get_all_users_of_tags(tag_ids)
    except TagsNotFound as tnf: raise tnf
    except Exception as e: raise e