from pydantic.main import BaseModel
from starlette.responses import JSONResponse
from api.container import get_dependencies
from fastapi import APIRouter, status
from core.items.services import item_service
from pydantic import BaseModel, Field

repo = get_dependencies().item_repo

router = APIRouter()

class ItemResponse(BaseModel):
    title: str = Field(..., description="test")

@router.get(
    "/item",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    tags=["Test Item"],
    summary="Test Item",
    description="Item Test.",
)
async   def test_item():
    return {
        "title": await item_service.create(repo, "testlowercase"),
    }