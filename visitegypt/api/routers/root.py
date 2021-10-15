from enum import Enum

from fastapi import status
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field

from visitegypt.config.environment import PROJECT_NAME, API_PREFIX

from visitegypt.api.routers.account.user import router as userRouter
from visitegypt.api.routers.item.item import router as itemRouter
from visitegypt.api.routers.place.place import router as placeRouter

router = APIRouter()

router.include_router(userRouter, prefix="/user")
router.include_router(itemRouter, prefix="/item")
router.include_router(placeRouter, prefix="/place")

class StatusEnum(str, Enum):
    OK = "OK"
    FAILURE = "FAILURE"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class HealthCheck(BaseModel):
    title: str = Field(..., description="API title")
    description: str = Field(..., description="Brief description of the API")
    version: str = Field(..., description="API server version number")
    status: StatusEnum = Field(..., description="API current status")


@router.get(
    "/status",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    tags=["Health Check"],
    summary="Performs health check",
    description="Performs health check and returns information about running service.",
)
def health_check():
    return {
        "title": PROJECT_NAME,
        "description": "This is a test desc",
        "version": API_PREFIX,
        "status": StatusEnum.OK,
    }

