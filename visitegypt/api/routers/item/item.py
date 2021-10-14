from fastapi import APIRouter, status, HTTPException
from loguru import logger
from visitegypt.api.container import get_dependencies
from visitegypt.core.items.services import item_service
from visitegypt.core.items.entities.item import ItemsPageResponse
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.item_error import *

repo = get_dependencies().item_repo

router = APIRouter(tags=['Item'])


@router.get(
    "/",
    response_model=ItemsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all items"
)
async def get_items(page_num : int = 1, limit : int = 15):
    try:
        return await item_service.get_all_items_paged(repo, page_num=page_num, limit=limit)
    except Exception as e:
        if isinstance(e, ItemNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Items"))
        else: raise e
