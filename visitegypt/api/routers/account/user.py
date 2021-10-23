from visitegypt.api.container import get_dependencies
from fastapi import APIRouter, HTTPException, Security, Depends, status
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UsersPageResponse,
)
from visitegypt.core.authentication.entities.userauth import UserAuthBody
from visitegypt.core.authentication.services.auth_service import (
    login_access_token as login_service,
)
from visitegypt.core.errors.user_errors import (
    UserNotFoundError,
    EmailNotUniqueError,
    WrongEmailOrPassword
)
from visitegypt.resources.strings import (
    EMAIL_TAKEN,
    INCORRECT_LOGIN_INPUT,
    MESSAGE_404,
)
from visitegypt.core.authentication.entities.token import Token, RefreshRequest
from pydantic import EmailStr
from visitegypt.api.utils import get_current_user
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.authentication.services.auth_service import get_refreshed_token
repo = get_dependencies().user_repo


router = APIRouter(responses=generate_response_for_openapi("User"))


# Handlers
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["User"])
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
def refresh_token(refresh_request: RefreshRequest):
    print("haha")
    try:
        return get_refreshed_token(refresh_token=refresh_request.refresh_token,access_token=refresh_request.access_token)
    except Exception as e:
        raise e