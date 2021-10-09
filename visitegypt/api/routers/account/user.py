from visitegypt.api.container import get_dependencies
from fastapi import APIRouter,HTTPException, Security, Depends
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import UserCreate,UserResponse,UserUpdate,UserUpdaterole
from visitegypt.core.accounts.services.exceptions import EmailNotUniqueError, UserNotFoundError
from visitegypt.resources.strings import USER_DOES_NOT_EXIST_ERROR, EMAIL_TAKEN
from visitegypt.api.routers.account.auth import router as AuthRouter
from visitegypt.core.authentication.entities.token import Token
from pydantic import EmailStr
from visitegypt.api.routers.account.util import get_current_user
from visitegypt.core.accounts.entities.roles import *

repo = get_dependencies().user_repo

router = APIRouter(tags=["User"])
router.include_router(AuthRouter)

# Handlers
@router.post(
    "/register", response_model=Token
)
async def register_user(new_user: UserCreate):
    try:
        return await user_service.register(repo, new_user)

    except Exception as err:
        if isinstance(err, EmailNotUniqueError): raise HTTPException(409, detail=EMAIL_TAKEN)
        else: raise HTTPException(422, detail=str(err))

@router.get("/", response_model=UserResponse)
async def get_user(user_id: str=None,user_email: EmailStr=None, current_user: UserResponse = Depends(get_current_user)):
    if user_email == current_user.email or current_user.user_role == "ADMIN" or current_user.user_role == "SUPER_ADMIN":
        try:
            if user_id:
                return await user_service.get_user_by_id(repo, user_id)
            elif user_email:
                return await user_service.get_user_by_email(repo, user_email)
            else:
                raise HTTPException(422, detail="No Query Parameter Provided")
        except Exception as e:
            if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
            else: raise HTTPException(422, detail=str(e))
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
        else: raise HTTPException(422, detail=str(e))