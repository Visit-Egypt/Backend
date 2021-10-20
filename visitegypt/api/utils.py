from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from typing import Optional, List
import json
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.config.environment import SECRET_KEY, ALGORITHM
from visitegypt.core.authentication.entities.token import TokenPayload
from visitegypt.core.accounts.services.user_service import get_user_by_id
from loguru import logger
from visitegypt.api.container import get_dependencies
from collections import ChainMap
from bson import ObjectId


repo = get_dependencies().user_repo

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="api/user/auth/login",
    scopes={
        Role.USER["name"]: Role.USER["description"],
        Role.ACCOUNT_ADMIN["name"]: Role.ACCOUNT_ADMIN["description"],
        Role.ACCOUNT_MANAGER["name"]: Role.ACCOUNT_MANAGER["description"],
        Role.ADMIN["name"]: Role.ADMIN["description"],
        Role.SUPER_ADMIN["name"]: Role.SUPER_ADMIN["description"],
    },
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(reusable_oauth2),
) -> UserResponse:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        if payload.get("user_id") is None:
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await get_user_by_id(repo, token_data.user_id)

    if not user:
        raise credentials_exception
    if security_scopes.scopes and not token_data.role:
        raise HTTPException(
            status_code=401,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    if security_scopes.scopes and token_data.role not in security_scopes.scopes:
        raise HTTPException(
            status_code=401,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user


def filters_dict(filters: Optional[List[str]] = Query(None)):
    try:
        return list(map(json.loads, filters))  # If fails, returns JSONDECODEERROR
    except Exception:
        return []


async def common_parameters(
    q: Optional[List] = Depends(filters_dict), page_num: int = 1, limit: int = 10
):
    dict_of_filters = dict(ChainMap(*q))
    if "_id" not in dict_of_filters and "id" in dict_of_filters:
        dict_of_filters["_id"] = ObjectId(dict_of_filters.pop("id"))
    filter_filters_from_none = {k: v for k, v in dict_of_filters.items() if v}
    return {"filters": filter_filters_from_none, "page_num": page_num, "limit": limit}
