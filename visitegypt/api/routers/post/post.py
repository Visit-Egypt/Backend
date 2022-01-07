from fastapi import APIRouter, status, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.core.posts.sevices import post_service
from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)

from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.api.utils import get_current_user
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.post_error import PostNotFoundError
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
repo = get_dependencies().post_repo

router = APIRouter(responses=generate_response_for_openapi("Post"))


@router.get(
    "/{place_id}",
    response_model=PostsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get place posts",
    tags=["Post"]
)
async def get_place_posts(place_id, page_num: int = 1, limit: int = 15):
    try:
        return await post_service.get_place_posts_paged(
            place_id,repo, page_num=page_num, limit=limit
        )
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Posts"))
    except Exception as e: raise e

@router.get(
    "/user/{user_id}",
    response_model=PostsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user posts",
    tags=["Post"]
)
async def get_user_posts(user_id, page_num: int = 1, limit: int = 15):
    try:
        return await post_service.get_user_posts_paged(
            user_id,repo, page_num=page_num, limit=limit
        )
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Posts"))
    except Exception as e: raise e

@router.get(
    "/place/{post_id}",
    response_model=PostInDB,
    status_code=status.HTTP_200_OK,
    summary="Get Post",
    tags=["Post"]
)
async def get_post_by_id(post_id):
    try:
        return await post_service.get_post_by_id(repo, post_id)
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Post"))
    except Exception as e: raise e

@router.post(
    "/",
    response_model=PostInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Add new Post",
    tags=["Post"]
)
async def add_new_post(
    new_post: PostBase,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await post_service.create_place(repo, new_post)
    except Exception as e:
        raise e

@router.put(
    "/{post_id}",
    response_model=PostInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Update a Post",
    tags=["Post"]
)
async def update_post(
    post_id: str,
    post_to_update: UpdatePost,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"]],
    ),
):
    try:
        return await post_service.update_post(repo, post_to_update, post_id,str(current_user.id))
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Post"))
    except Exception as e: raise e

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Post", tags=["Post"])
async def delete_post(
    post_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        user_id = str(current_user.id)
        if(current_user.user_role == Role.SUPER_ADMIN["name"] or current_user.user_role == Role.ADMIN["name"]):
            user_id = current_user.user_role
        await post_service.delete_post(repo, post_id, user_id)
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Post"))
    except Exception as e: raise e

@router.post(
    "/like/{post_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add new like to a post",
    tags=["Post"]
)
async def add_new_like(
    post_id,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await post_service.add_like(repo, post_id, str(current_user.id))
    except Exception as e:
        raise e

@router.delete(
    "/like/{post_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a like from a post",
    tags=["Post"]
)
async def delete_post_like(
    post_id,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await post_service.delete_like(repo, post_id, str(current_user.id))
    except Exception as e:
        raise e
