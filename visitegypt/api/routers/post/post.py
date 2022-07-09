from typing import Dict
from fastapi import APIRouter, status, HTTPException, Security
from fastapi.params import Depends
from visitegypt.api.container import get_dependencies
from visitegypt.core.posts.sevices import post_service
from visitegypt.core.posts.entities.post import (
    PostInDB,
    PostsPageResponse,
    PostBase,
    UpdatePost,
)
from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse
from visitegypt.core.errors.upload_error import ResourceNotFoundError
from visitegypt.core.utilities.services import upload_service

from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.api.utils import get_current_user, common_parameters
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.post_error import PostNotFoundError, PostOffensive
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi

repo = get_dependencies().post_repo
upload_repo = get_dependencies().upload_repo

router = APIRouter(responses=generate_response_for_openapi("Post"))


@router.get(
    "/",
    response_model=PostsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Posts By Filter",
    tags=["Post"]
)
async def get_posts(params: Dict = Depends(common_parameters)):
    try:
        if params["page_num"] < 1 or params["limit"] < 1:
            raise HTTPException(422, "Query Params shouldn't be less than 1")
        return await post_service.get_filtered_post(
            repo=repo,
            page_num=params["page_num"],
            limit=params["limit"],
            filters=params["filters"],
        )
    except PostNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Posts"))
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
    except PostOffensive:
        raise HTTPException(status_code= 400, detail="Offensive post, please change it")
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


@router.get("/{post_id}/upload-photo", response_model = UploadResponse, status_code=status.HTTP_200_OK, tags=["Post"])
async def upload_post_photo(post_id: str, content_type: str, 
        current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    )):
    try:
        # Send data to the upload service.
        upload_req : UploadRequest = UploadRequest(user_id=current_user.id, resource_id=post_id, resource_name='posts', content_type=content_type)
        return await upload_service.generate_presigned_url(upload_repo, upload_req)
    except ResourceNotFoundError: raise HTTPException(404, detail="You are trying to upload in unknown resource")
