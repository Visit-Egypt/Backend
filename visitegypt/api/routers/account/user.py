from visitegypt.api.container import get_dependencies
from fastapi import APIRouter,HTTPException
from visitegypt.core.accounts.services import user_service
from visitegypt.core.accounts.entities.user import UserCreate,UserResponse
from visitegypt.core.accounts.services.exceptions import EmailNotUniqueError, UserNotFoundError
from visitegypt.resources.strings import USER_DOES_NOT_EXIST_ERROR, EMAIL_TAKEN
from visitegypt.api.routers.account.auth import router as AuthRouter

repo = get_dependencies().user_repo

router = APIRouter()
router.include_router(AuthRouter)

# Handlers
@router.post(
    "/register", response_model=UserResponse
)
async def register_user(new_user: UserCreate):
    try:
        return await user_service.register(repo, new_user)
    except Exception as err:
        if isinstance(err, EmailNotUniqueError): raise HTTPException(409, detail=EMAIL_TAKEN)
        else: raise HTTPException(422, detail=str(err))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        return await user_service.get_user_by_id(repo, user_id)
    except Exception as e:
        if isinstance(e, UserNotFoundError): raise HTTPException(404, detail=USER_DOES_NOT_EXIST_ERROR)
        else: raise HTTPException(422, detail=str(e))

