from pydantic.main import BaseModel
from starlette.responses import JSONResponse
from visitEgypt.api.container import get_dependencies
from fastapi import APIRouter, status
from visitEgypt.core.items.services import item_service
from pydantic import BaseModel, Field
from loguru import logger

repo = get_dependencies().item_repo

router = APIRouter()

class ItemResponse(BaseModel):
    title: str = Field(..., description="test")

@router.get(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    tags=["Test Item"],
    summary="Endpoint Summary",
    description="Item Test.",
)
async   def test_item():
    logger.info("This is a log test")
    return {
        "title": await item_service.create(repo, "testlowercase"),
    }