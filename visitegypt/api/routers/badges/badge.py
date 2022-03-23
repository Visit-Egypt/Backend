from fastapi import APIRouter, status, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.core.badges.services import badge_service
from fastapi.params import Depends
from visitegypt.core.badges.entities.badge import (
    BadgeBase,
    BadgeTask,
    BadgesPageResponse,
    BadgeInDB,
    BadgeUpdate
)
from visitegypt.core.utilities.services import upload_service
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.badge_error import BadgeNotFoundError,BadgeAlreadyExists
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.utils import common_parameters, get_current_user
from typing import Dict
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.core.accounts.entities.roles import Role

repo = get_dependencies().badge_repo

router = APIRouter(responses=generate_response_for_openapi("Badge"))

@router.get(
    "/",
    #response_model=BadgesPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all Badges",
    tags=["Bage"]
)
async def get_items(params: Dict = Depends(common_parameters)):
    try:
        if params["page_num"] < 1 or params["limit"] < 1:
            raise HTTPException(422, "Query Params shouldn't be less than 1")
        return await badge_service.get_filtered_badges(
            repo,
            page_num=params["page_num"],
            limit=params["limit"],
            filters=params["filters"],
        )
    except BadgeNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Item"))
    except Exception as e: raise e

@router.post(
    "/",
    response_model=BadgeInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Add new Badge",
    tags=["Admin Panel"]
)
async def add_new_badge(
    badge_to_create: BadgeBase,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await badge_service.create_badge(repo, badge_to_create)
    except BadgeAlreadyExists: raise HTTPException(409, detail="Badge Already exists")
    except BadgeNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Badge"))
    except Exception as e: raise e

@router.put(
    "/{badge_id}",
    response_model=BadgeInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Update a Badge",
    tags=["Admin Panel"]
)
async def update_badge(
    badge_id: str,
    badge_to_update: BadgeUpdate,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await badge_service.update_badge_by_id(
            repo, badge_id=badge_id, badge_to_update=badge_to_update
        )
    except BadgeNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Badge"))
    except Exception as e: raise e

@router.delete(
    "/{badge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Badge",
    tags=["Admin Panel"]
)
async def delete_badge(
    badge_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        await badge_service.delete_badge_by_id(repo, badge_id)
    except BadgeNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Badge"))
    except Exception as e: raise e