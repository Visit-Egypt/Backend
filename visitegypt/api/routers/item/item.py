from typing import Dict
from fastapi import APIRouter, status, HTTPException, Security
from fastapi.params import Depends
from visitegypt.api.container import get_dependencies
from visitegypt.core.items.services import item_service
from visitegypt.core.items.entities.item import (
    ItemBase,
    ItemInDB,
    ItemUpdate,
    ItemsPageResponse,
)
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.item_error import ItemNotFoundError, ItemAlreadyExists
from visitegypt.api.utils import common_parameters, get_current_user
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi

repo = get_dependencies().item_repo

router = APIRouter(responses=generate_response_for_openapi("Item"))


@router.get(
    "/",
    response_model=ItemsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all items",
    tags=["Item"]
)
async def get_items(params: Dict = Depends(common_parameters)):
    try:
        if params["page_num"] < 1 or params["limit"] < 1:
            raise HTTPException(422, "Query Params shouldn't be less than 1")
        return await item_service.get_filtered_items(
            repo,
            page_num=params["page_num"],
            limit=params["limit"],
            filters=params["filters"],
        )
    except ItemNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Item"))
    except Exception as e: raise e

@router.post(
    "/",
    response_model=ItemInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Add new Item",
    tags=["Admin Panel"]
)
async def add_new_item(
    item_to_create: ItemBase,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await item_service.create_item(repo, item_to_create)
    except ItemAlreadyExists: raise HTTPException(409, detail="Item Already exists")
    except ItemNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Item"))
    except Exception as e: raise e


@router.put(
    "/{item_id}",
    response_model=ItemInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Update an Item",
    tags=["Admin Panel"]
)
async def update_item(
    item_id: str,
    item_to_update: ItemUpdate,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await item_service.update_item_by_id(
            repo, item_id=item_id, item_to_update=item_to_update
        )
    except ItemNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Item"))
    except Exception as e: raise e


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an Item",
    tags=["Admin Panel"]
)
async def delete_item(
    item_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        await item_service.delete_item_by_id(repo, item_id)
    except ItemNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Item"))
    except Exception as e: raise e