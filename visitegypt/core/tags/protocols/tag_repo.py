from typing import List, Optional, Protocol
from typing import Dict, Protocol
from visitegypt.core.tags.entities.tag import Tag, TagUpdate
from visitegypt.core.accounts.entities.user import UserResponseInTags

class TagRepo(Protocol):
    async def get_all_tags(self, filters: Dict) -> List[Tag]:
        pass
    async def add_tag(self, new_tag: Tag) -> Optional[Tag]:
        pass
    async def update_tag(self, update_tag: TagUpdate, tag_id: str) -> Optional[Tag]:
        pass
    async def delete_tag(self, tag_id: str) -> Optional[bool]:
        pass

    async def get_all_users_of_tags(self, tag_ids: List[str]) -> Optional[List[UserResponseInTags]]:
        pass