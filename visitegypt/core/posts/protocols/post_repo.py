from typing import Protocol, Optional
from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)


class PostRepo(Protocol):
    async def get_place_posts(self, page_num: int, limit: int, place_id:str) -> PostsPageResponse:
        pass

    async def get_post_by_id(post_id: str) -> Optional[PostInDB]:
        pass

    async def create_post(new_post: PostBase) -> PostInDB:
        pass

    async def delete_post(post_id: str, user_id:str):
        pass

    async def update_post(
        updated_post: UpdatePost, post_id: str,user_id: str
    ) -> Optional[PostInDB]:
        pass

    async def add_like(post_id: str,user_id:str):
        pass

    async def delete_like(post_id: str,user_id:str):
        pass
