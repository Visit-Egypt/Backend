from fastapi import APIRouter, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.api.routers.account.util import get_current_user
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.core.authentication.entities.token import Token
from visitegypt.core.authentication.entities.userauth import UserAuthBody
from visitegypt.core.authentication.services.auth_service import login_access_token as login_service
from visitegypt.core.authentication.services.exceptions import WrongEmailOrPassword
from visitegypt.resources.strings import INCORRECT_LOGIN_INPUT
from visitegypt.core.accounts.entities.roles import *

router = APIRouter(prefix="/auth", tags=["auth"])

repo = get_dependencies().user_repo


@router.post("/login", response_model=Token)
async def login_access_token_r(
    auth_body: UserAuthBody
):
    try:
        return await login_service(repo, auth_body)
    except Exception as err:
        if isinstance(err, WrongEmailOrPassword): raise HTTPException(409, detail=INCORRECT_LOGIN_INPUT)
        else:
            raise HTTPException(422, detail=str(err))

@router.get("/testscopes", response_model= UserResponse)
async def test_scope( 
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]],
    )):
    return current_user