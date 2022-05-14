from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)
from visitegypt.core.posts.protocols.post_repo import PostRepo
from typing import Dict, Optional
from visitegypt.core.errors.post_error import PostNotFoundError


async def get_filtered_post(
    repo: PostRepo, page_num: int = 1, limit: int = 15, filters: Dict = None
) -> PostsPageResponse:
    try:
        post = await repo.get_filtered_post(page_num=page_num, limit=limit, filters=filters)
        if post:
            return post
        raise PostNotFoundError
    except PostNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e

async def create_place(repo: PostRepo, new_post: PostBase) -> PostInDB:
    try:
        return await repo.create_post(new_post)
    except Exception as e:
        raise e


async def delete_post(repo: PostRepo, post_id: str, user_id:str):
    try:
        return await repo.delete_post(post_id,user_id)
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def update_post(
    repo: PostRepo, post_to_update: UpdatePost, post_id: str, user_id:str
) -> Optional[PostInDB]:
    try:
        return await repo.update_post(post_to_update, post_id,user_id)
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def add_like(repo: PostRepo,post_id: str,user_id:str):
    try:
        return await repo.add_like(post_id,user_id)
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def delete_like(repo: PostRepo,post_id: str,user_id:str):
    try:
        return await repo.delete_like(post_id,user_id)
    except PostNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e