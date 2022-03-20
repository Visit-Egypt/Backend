from visitegypt.api.container import get_dependencies
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Security, Depends, status
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UsersPageResponse,
    Badge,
    BadgeTask,
    BadgeUpdate,PlaceActivityUpdate,PlaceActivity,BadgeResponse
)
from visitegypt.core.authentication.entities.userauth import UserAuthBody
from visitegypt.core.authentication.services.auth_service import (
    login_access_token as login_service,
)
from visitegypt.core.errors.upload_error import ResourceNotFoundError
from visitegypt.core.utilities.services import upload_service
from visitegypt.core.errors.user_errors import (
    UserNotFoundError,
    EmailNotUniqueError,
    WrongEmailOrPassword
)
from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse
from visitegypt.resources.strings import (
    EMAIL_TAKEN,
    INCORRECT_LOGIN_INPUT,
    MESSAGE_404,
)
from visitegypt.core.authentication.entities.token import Token, RefreshRequest
from pydantic import EmailStr
from visitegypt.api.utils import get_current_user,get_refreshed_token
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.errors.http_error import HTTPErrorModel
repo = get_dependencies().user_repo
upload_repo = get_dependencies().upload_repo

router = APIRouter(responses=generate_response_for_openapi("User"))


# Handlers
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["User"], responses={**generate_response_for_openapi("User"), 409: {
    "model": HTTPErrorModel,
    "description": "User with this email already exists",
    "content": {
        "application/json": {
        "example": {"errors": ["User with this email already exists"], "status_code": "409"}
        }
     }   
    }})
async def register_user(new_user: UserCreate):
    try:
        return await user_service.register(repo, new_user)
    except EmailNotUniqueError: raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN)
    except Exception as err: raise err


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK, tags=["User"])
async def get_user(
    user_id: str = None,
    user_email: EmailStr = None,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
):
    if (
        user_email == current_user.email
        or str(user_id) == str(current_user.id)
        or current_user.user_role == Role.ADMIN["name"]
        or current_user.user_role == Role.SUPER_ADMIN["name"]
    ):
        try:
            if user_id:
                return await user_service.get_user_by_id(repo, user_id)
            elif user_email:
                return await user_service.get_user_by_email(repo, user_email)
            else:
                raise HTTPException(422, detail="No Query Parameter Provided")
        except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
        except Exception as e: raise e
    else:
        raise HTTPException(401, detail="Unautherized")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin Panel"])
async def delete_user(
    user_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"]],
    ),
):
    try:
        await user_service.delete_user_by_id(repo, user_id)
    except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as e: raise e


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["User"])
async def update_user(
    user_id: str,
    updated_user: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    if str(user_id) == str(current_user.id):
        try:
            return await user_service.update_user_by_id(repo, updated_user, user_id)
        except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
        except Exception as e: raise e
    else:
        raise HTTPException(401, detail="Unautherized")


@router.put("/role/{user_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admin Panel"])
async def update_user_role(
    user_id: str,
    updated_user_role: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"]],
    ),
):
    try:
        if updated_user_role:
            return await user_service.update_user_role(repo, updated_user_role, user_id)
        else: raise HTTPException(422, "No Query Params Specified")
    except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as e: raise e


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, tags=["User"])
async def login_user(auth_body: UserAuthBody):
    try:
        return await login_service(repo, auth_body)
    except WrongEmailOrPassword:
        raise HTTPException(401, detail=INCORRECT_LOGIN_INPUT)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err:
        raise err


@router.get("/all", response_model=UsersPageResponse, status_code=status.HTTP_200_OK, tags=["Admin Panel"])
async def get_all_users(
    page_num: int = 1,
    limit: int = 15,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
):
    try:
        return await user_service.get_all_users(repo, page_num=page_num, limit=limit)
    except Exception as e:
        raise e

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK, tags=["User"])
async def refresh_token(refresh_request: RefreshRequest):
    try:
        return await get_refreshed_token(repo=repo,refresh_token=refresh_request.refresh_token,access_token=refresh_request.access_token)
    except Exception as e:
        raise e

@router.post("/logout/{user_id}", status_code=status.HTTP_200_OK, tags=["User"])
async def user_logout(user_id: str,current_user: UserResponse = Depends(get_current_user)):
    if str(user_id) == str(current_user.id):
        try:
            await repo.user_logout(user_id=user_id)
            return "User Loged Out"
        except Exception as e:
            raise e
    else:
        raise HTTPException(401, detail="Unautherized")
"""
, 
        current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    )
"""
@router.get("/{user_id}/upload-photo", response_model = UploadResponse, status_code=status.HTTP_200_OK, tags=["User"])
async def upload_user_personal_photo(user_id: str, content_type: str, 
        current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    )):
    if str(user_id) == str(current_user.id):
        try:
            # Send data to the upload service.
            upload_req : UploadRequest = UploadRequest(user_id=user_id, resource_id=user_id, resource_name='users', content_type=content_type)
            return await upload_service.generate_presigned_url(upload_repo, upload_req)
        except ResourceNotFoundError: raise HTTPException(404, detail="You are trying to upload in unknown resource")
    else:
        raise HTTPException(401, detail="Unautherized")

@router.put(
    "/badge/task",
    summary="Update badge task progress for a user",
    tags=["User"]
)
async def update_badge_task_progress(
    new_task: BadgeTask,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.update_badge_task(repo, current_user.id, new_task)
    except Exception as e:
        raise e

@router.put(
    "/badges/{badge_id}",
    summary="Update badge for a user",
    tags=["User"]
)
async def update_badge(
    new_badge: BadgeUpdate,
    badge_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.update_badge(repo, current_user.id, badge_id,new_badge)
    except Exception as e:
        raise e

@router.get(
    "/badges/{user_id}",
    response_model = List[BadgeResponse],
    summary="get badges of a user",
    tags=["User"]
)
async def get_user_badges(
    user_id:str):
    try:
        return await user_service.get_user_badges(repo, user_id)
    except Exception as e:
        raise e

@router.put(
    "/actvity/{activity_id}",
    summary="Update Place Activity for a user",
    tags=["User"]
)
async def update_place_avtivity(
    new_activity: PlaceActivity,
    activity_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.update_place_activity(repo, current_user.id, activity_id,new_activity)
    except Exception as e:
        raise e

@router.get(
    "/actvity/{user_id}",
    summary="get place activities of a user",
    tags=["User"]
)
async def get_user_activities(
    user_id:str):
    try:
        return await user_service.get_user_activities(repo, user_id)
    except Exception as e:
        raise e