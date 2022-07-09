from typing import Protocol, Optional, Dict
from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)


class PostRepo(Protocol):
    async def get_filtered_post(page_num: int, limit: int, filters: Dict = None) -> PostsPageResponse:
        pass

    async def create_post(self, new_post: PostBase) -> PostInDB:
        pass

    async def delete_post(self, post_id: str, user_id:str):
        pass

    async def update_post(
        self, updated_post: UpdatePost, post_id: str,user_id: str
    ) -> Optional[PostInDB]:
        pass

    async def add_like(self, post_id: str,user_id:str):
        pass

    async def delete_like(self,post_id: str,user_id:str):
        pass
