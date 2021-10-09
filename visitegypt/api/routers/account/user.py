from visitegypt.api.container import get_dependencies
from fastapi import APIRouter,HTTPException, Security, Depends
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import UserCreate,UserResponse,UserUpdate,UserUpdaterole
from visitegypt.core.authentication.entities.userauth import UserAuthBody
from visitegypt.core.authentication.services.auth_service import login_access_token as login_service
from visitegypt.core.errors.user_errors import *
from visitegypt.resources.strings import USER_DOES_NOT_EXIST_ERROR, EMAIL_TAKEN, INCORRECT_LOGIN_INPUT
from visitegypt.core.authentication.entities.token import Token
from pydantic import EmailStr
from visitegypt.api.routers.account.util import get_current_user
from visitegypt.core.accounts.entities.roles import *

repo = get_dependencies().user_repo

router = APIRouter(tags=["User"])

# Handlers
@router.post(
    "/register", response_model=Token
)
async def register_user(new_user: UserCreate):
    try:
        return await user_service.register(repo, new_user)

    except Exception as err:
        if isinstance(err, EmailNotUniqueError): raise HTTPException(409, detail=EMAIL_TAKEN)
        else: raise err

@router.get("/", response_model=UserResponse)
async def get_user(user_id: str=None,user_email: EmailStr=None,current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"],Role.ADMIN["name"],Role.SUPER_ADMIN["name"]],
    )):
    if user_email == current_user.email or user_id == current_user.id:
        try:
            if user_id:
                return await user_service.get_user_by_id(repo, user_id)
            elif user_email:
                return await user_service.get_user_by_email(repo, user_email)
            else:
                raise HTTPException(422, detail="No Query Parameter Provided")
        except Exception as e:
            if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
            else: raise e
    else:
        raise HTTPException(401, detail="Unautherized")
    
@router.delete("/{user_id}")
async def delete_user(user_id: str,current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"]],
    )):
    try:
        return await user_service.delete_user_by_id(repo, user_id)
    except Exception as e:
        if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
        else: raise HTTPException(422, detail=str(e))

@router.put("/{user_id}")
async def update_user(user_id: str,updated_user: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    if user_id == current_user.id:
        try:
            return await user_service.update_user_by_id(repo,updated_user, user_id)
        except Exception as e:
            if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
            else: raise HTTPException(422, detail=str(e))
    else:
        raise HTTPException(401, detail="Unautherized")

@router.put("/role/{user_id}")
async def update_user(user_id: str,updated_user: UserUpdaterole,current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"]],
    )):
    try:
        return await user_service.update_user_role(repo,updated_user, user_id)
    except Exception as e:
        if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
        else: raise e

@router.post("/login", response_model=Token)
async def login_user(
    auth_body: UserAuthBody
):
    try:
        return await login_service(repo, auth_body)
    except Exception as err:
        if isinstance(err, WrongEmailOrPassword): raise HTTPException(409, detail=INCORRECT_LOGIN_INPUT)
        else:
            raise err

