from typing import List, Optional, Protocol
from typing import Dict, Protocol
from visitegypt.core.tags.entities.tag import Tag, TagUpdate

class TagRepo(Protocol):
    async def get_all_tags(self, filters: Dict) -> List[Tag]:
        pass
    async def add_tag(self, new_tag: Tag) -> Optional[Tag]:
        pass
    async def update_tag(self, update_tag: TagUpdate, tag_id: str) -> Optional[Tag]:
        pass
    async def delete_tag(self, tag_id: str) -> Optional[bool]:
        pass

     