from visitegypt.api.container import get_dependencies
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Security, Depends, status, Request, Query
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UsersPageResponse,
    Badge,
    BadgeResponseDetail,
    BadgeTask,
    BadgeUpdate,PlaceActivityUpdate,PlaceActivity,BadgeResponse,RequestTripMate, UserPrefsReq, UserFollowResp
)
from visitegypt.core.authentication.entities.userauth import UserAuthBody,UserGoogleAuthBody,UserPasswordReset
from visitegypt.core.authentication.services.auth_service import (
    login_access_token as login_service,
)
from visitegypt.core.authentication.services.auth_service import login_google_access_token
from visitegypt.core.errors.upload_error import ResourceNotFoundError
from visitegypt.core.utilities.services import upload_service
from visitegypt.core.errors.user_errors import (
    UserNotFoundError,
    EmailNotUniqueError,
    WrongEmailOrPassword, 
    TripRequestNotFound,
    UserIsFollower,
    UserIsNotFollowed
)
from visitegypt.core.errors.tag_error import TagsNotFound
from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse
from visitegypt.resources.strings import (
    EMAIL_TAKEN,
    INCORRECT_LOGIN_INPUT,
    MESSAGE_404,
)
from visitegypt.core.authentication.entities.token import Token, RefreshRequest
from pydantic import EmailStr
from visitegypt.api.utils import get_current_user,get_refreshed_token, common_parameters
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.errors.http_error import HTTPErrorModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.security import OAuth2PasswordRequestForm
repo = get_dependencies().user_repo
upload_repo = get_dependencies().upload_repo

router = APIRouter(responses=generate_response_for_openapi("User"))
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

# Handlers
@router.post("/register", status_code=status.HTTP_201_CREATED, tags=["User"], responses={**generate_response_for_openapi("User"), 409: {
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
        return await user_service.new_register(repo, new_user)
    except EmailNotUniqueError: raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN)
    except Exception as err: raise err

@router.get("/forgotpassword/{email}", status_code=status.HTTP_201_CREATED, tags=["User"])
async def reset_password(email:str):
    try:
        return await user_service.forgot_password(repo, email)
    except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err: raise err

@router.get("/resetpassword/{user_id}/{token}", status_code=status.HTTP_201_CREATED, tags=["User"], response_class=HTMLResponse, include_in_schema=False)
async def reset_password(request: Request,user_id:str,token:str):
    try:
        await user_service.check_user_id(repo,user_id,token)
        return TEMPLATES.TemplateResponse("reset_password.html", {"request": request,"user_id": user_id, "token": token})
    except Exception as err: raise err

@router.post("/resetpassword/{user_id}/{token}", status_code=status.HTTP_201_CREATED, tags=["User"], include_in_schema=False)
async def reset_password(user_id:str,token:str,new_password:UserPasswordReset):
    try:
        return await user_service.reset_password(repo,user_id,token,new_password.password)
    except Exception as err: raise err

@router.get("/verfiy/{token}", status_code=status.HTTP_201_CREATED, tags=["User"], include_in_schema=False)
async def create_user(token:str):
    try:
        return await user_service.create_user(repo, token)
    except EmailNotUniqueError: raise HTTPException(status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN)
    except Exception as err: raise err

@router.post("/register/google", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["User"], responses={**generate_response_for_openapi("User"), 409: {
    "model": HTTPErrorModel,
    "description": "User with this email already exists",
    "content": {
        "application/json": {
        "example": {"errors": ["User with this email already exists"], "status_code": "409"}
        }
     }   
    }})
async def register_user(new_user: UserGoogleAuthBody):
    try:
        return await user_service.google_register(repo, new_user)
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
    try:
        if user_id:
            return await user_service.get_user_by_id(repo, user_id)
        elif user_email:
            return await user_service.get_user_by_email(repo, user_email)
        else:
            raise HTTPException(422, detail="No Query Parameter Provided")
    except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as e: raise e


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

@router.post("/login/swagger", response_model=Token, status_code=status.HTTP_200_OK, tags=["User"])
async def login_user(request: OAuth2PasswordRequestForm = Depends()):
    try:
        auth_body = UserAuthBody(email=request.username,password=request.password)
        return await login_service(repo, auth_body)
    except WrongEmailOrPassword:
        raise HTTPException(401, detail=INCORRECT_LOGIN_INPUT)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err:
        raise err

@router.post("/login/google", response_model=Token, status_code=status.HTTP_200_OK, tags=["User"])
async def login_user(token: UserGoogleAuthBody):
    try:
        return await login_google_access_token(repo, token)
    except WrongEmailOrPassword:
        raise HTTPException(401, detail=INCORRECT_LOGIN_INPUT)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err:
        raise err


@router.get("/all", response_model=UsersPageResponse, status_code=status.HTTP_200_OK, tags=["Admin Panel"])
async def get_all_users(
    params: Dict = Depends(common_parameters),
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    ),
):
    try:
        if params["page_num"] < 1 or params["limit"] < 1:
            raise HTTPException(422, "Query Params shouldn't be less than 1")
        return await user_service.get_all_users(
            repo,
            page_num=params["page_num"],
            limit=params["limit"],
            filters=params["filters"],
        )
    except UserNotFoundError as e: raise HTTPException(404, detail="User Not Found")
    except Exception as e: raise e

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

@router.get("/{user_id}/upload-ar", response_model = UploadResponse, status_code=status.HTTP_200_OK, tags=["User"])
async def upload_user_personal_photo(user_id: str, content_type: str):
    try:
        upload_req : UploadRequest = UploadRequest(user_id=user_id, resource_id=user_id, resource_name='ar', content_type=content_type)
        return await upload_service.generate_presigned_url(upload_repo, upload_req)
    except ResourceNotFoundError: raise HTTPException(404, detail="You are trying to upload in unknown resource")

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

@router.put(
    "/visitplace/{place_id}",
    summary="User Visit Place",
    tags=["User"]
)
async def visit_place(
    place_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.visit_place(repo, current_user.id, place_id)
    except Exception as e:
        raise e

@router.put(
    "/reviewplace/{place_id}",
    summary="User Review Place",
    tags=["User"]
)
async def review_place(
    place_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.review_place(repo, current_user.id, place_id)
    except Exception as e:
        raise e

@router.put(
    "/addpost/{place_id}",
    summary="User Added Post",
    tags=["User"]
)
async def add_post(
    place_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.add_post(repo, current_user.id, place_id)
    except Exception as e:
        raise e

@router.put(
    "/scanobject/{place_id}/{explore_id}",
    summary="User Scanned Object",
    tags=["User"]
)
async def add_post(
    place_id:str,
    explore_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.scan_object(repo, current_user.id, place_id,explore_id)
    except Exception as e:
        raise e

@router.put(
    "/chatbotartifact/{place_id}",
    summary="User ask chatbot about artifact",
    tags=["User"]
)
async def chatbot_artifact(
    place_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.chatbot_artifact(repo, current_user.id, place_id)
    except Exception as e:
        raise e

@router.put(
    "/chatbotplace/{place_id}",
    summary="User ask chatbot about place",
    tags=["User"]
)
async def chatbot_place(
    place_id:str,
    current_user: UserResponse = Depends(get_current_user)
    ):
    try:
        return await user_service.chatbot_place(repo, current_user.id, place_id)
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

@router.get(
    "/badgesdetail/{user_id}",
    response_model = List[BadgeResponseDetail],
    summary="get badges of a user with details",
    tags=["User"]
)
async def get_user_badges_detail(
    user_id:str):
    try:
        return await user_service.get_user_badges_detail(repo, user_id)
    except Exception as e:
        raise e

@router.put(
    "/actvity/{activity_id}",
    summary="Update Place Activity for a user",
    tags=["User"]
)
async def update_place_avtivity(
    new_activity: PlaceActivityUpdate,
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

@router.get(
    "/allactvitydetail/{user_id}",
    summary="get place activities and explores of a user with details",
    tags=["User"]
)
async def get_user_all_activities_detail(
    user_id:str,place_id: Optional[str] = Query(None)):
    try:
        return await user_service.get_user_activities_deatil(repo, user_id,place_id)
    except Exception as e:
        raise e

@router.get(
    "/actvitydetail/{user_id}",
    summary="get activities of a user with details",
    tags=["User"]
)
async def get_user_activities_detail(
    user_id:str,place_id: Optional[str] = Query(None)):
    try:
        return await user_service.get_user_only_activities_detail(repo, user_id,place_id)
    except Exception as e:
        raise e

@router.get(
    "/exploredetail/{user_id}",
    summary="get explores of a user with details",
    tags=["User"]
)
async def get_user_explores_detail(
    user_id:str,place_id: Optional[str] = Query(None)):
    try:
        return await user_service.get_user_only_explore_detail(repo, user_id,place_id)
    except Exception as e:
        raise e

@router.post('/{user_id}/follow', response_model = UserFollowResp, summary="Follow a user", tags=['User'])
async def follow_user(user_id: str, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.follow_user(repo, current_user, user_id)
    except UserIsFollower: raise HTTPException(400, detail='You already followed the user')
    except UserNotFoundError: raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err: raise err

@router.post('/{user_id}/unfollow', response_model = UserFollowResp, summary="Follow a user", tags=['User'])
async def unfollow_user(user_id: str, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.unfollow_user(repo, current_user, user_id)
    except UserIsNotFollowed: raise HTTPException(400, detail='You are not following the user')
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err:
        raise err

@router.post('/{user_id}/mate', summary="Request a trip mate", tags=['User'])
async def follow_user(user_id: str, request_mate: RequestTripMate, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.request_trip_mate(repo, current_user, user_id, request_mate)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err:
        raise err


@router.post('/trip-mate-reqs/{req_id}/approve', summary="Request a trip mate", tags=['User'])
async def follow_user(req_id: str, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.approve_request_trip_mate(repo, current_user, req_id)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except TripRequestNotFound: raise HTTPException(404, detail=MESSAGE_404("Trip Request not exists"))
    except Exception as err:
        raise err


@router.post('/interests', summary="Add prefs", tags=['User'])
async def add_prefs_user(prefs: UserPrefsReq, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.add_preferences(repo, current_user, prefs.pref_list)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except Exception as err: raise err


@router.post('/interests/delete', summary="Remove prefs", tags=['User'])
async def follow_user(prefs: UserPrefsReq, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        return await user_service.remove_preferences(repo, current_user, prefs.pref_list)
    except UserNotFoundError:
        raise HTTPException(404, detail=MESSAGE_404("User"))
    except TagsNotFound as ue: raise HTTPException(404, detail=MESSAGE_404("Tag"))
    except Exception as err: raise err