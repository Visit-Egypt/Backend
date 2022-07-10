from typing import List, Optional, Protocol
from typing import Dict, Protocol
from visitegypt.core.tags.entities.tag import Tag, TagUpdate, GetTagResponse
from visitegypt.core.accounts.entities.user import UserResponseInTags

class TagRepo(Protocol):
    async def get_all_tags(self, filters: Dict, lang: str) -> List[GetTagResponse]:
        pass
    async def add_tag(self, new_tag: Tag) -> Optional[GetTagResponse]:
        pass
    async def update_tag(self, update_tag: TagUpdate, tag_id: str) -> Optional[GetTagResponse]:
        pass
    async def delete_tag(self, tag_id: str) -> Optional[bool]:
        pass

    async def get_all_users_of_tags(self, tag_ids: List[str]) -> Optional[List[UserResponseInTags]]:
        pass
    async def register_tag_to_notification(tag_id: str) -> bool:
        pass