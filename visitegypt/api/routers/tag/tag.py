from typing import List, Dict
from fastapi import APIRouter, Depends, status, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.core.tags.services import tag_service
from visitegypt.core.tags.entities.tag import TagUpdate, Tag, TagCreation, UsersTagsReq, GetTagResponse
from visitegypt.core.errors.tag_error import TagsNotFound, TagCreationError, TagAlreadyExists
from visitegypt.core.accounts.entities.user import UserResponseInTags
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.utils import get_current_user, common_parameters
from visitegypt.resources.strings import MESSAGE_404


repo = get_dependencies().tag_repo
router = APIRouter(responses=generate_response_for_openapi("Tag"))

@router.get(
    "/",
    response_model=List[GetTagResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Tags",
    tags=["Tags"]
)
async def get_tags(params: Dict = Depends(common_parameters)):
    try:
        return await tag_service.get_all_tags(repo, params["filters"])
    except TagsNotFound: raise HTTPException(404, detail=MESSAGE_404("Tags"))
    except Exception as e: raise e


@router.post("/", response_model=GetTagResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary='Add new tag', 
    tags=["Tags"])
async def add_tag(new_tag: TagCreation):
    try:
        return await tag_service.add_new_tag(repo, new_tag)
    except TagAlreadyExists: raise HTTPException(409, detail="Tag already exists")
    except TagCreationError: raise HTTPException(400, detail="Tag creation error")
    except Exception as e: raise e


@router.put("/{tag_id}", response_model=GetTagResponse, status_code=status.HTTP_201_CREATED, tags=["Tags"])
async def update_tag(tag_id: str, updated_tag: TagUpdate):
    try:
        return await tag_service.update_tag(repo, updated_tag, tag_id)
    except TagsNotFound: raise HTTPException(404, detail=MESSAGE_404("Tag"))
    except Exception as e: raise e

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Tag", tags=["Tags"])
async def delete_post(tag_id: str):
    try:
        return await tag_service.delete_tag(repo, tag_id)
    except TagsNotFound: raise HTTPException(404, detail=MESSAGE_404("Tag"))
    except Exception as e: raise e

@router.post(
    "/users",
    response_model=List[UserResponseInTags],
    status_code=status.HTTP_200_OK,
    summary="Get All Tag users",
    tags=["Tags"]
)
async def get_tags(tags_ids : UsersTagsReq):
    try:
        return await tag_service.get_all_users_of_tags(repo, tags_ids.tags_ids)
    except TagsNotFound: raise HTTPException(404, detail=MESSAGE_404("Tags"))
    except Exception as e: raise e


@router.put("/register-notif/{tag_id}", response_model=GetTagResponse, status_code=status.HTTP_201_CREATED, tags=["Tags"])
async def register_tag_notifications(tag_id: str):
    try:
        return await tag_service.register_tag_to_notifications(repo, tag_id)
    except TagsNotFound: raise HTTPException(404, detail=MESSAGE_404("Tag"))
    except Exception as e: raise e