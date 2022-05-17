from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from typing import Optional, List
import json
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.config.environment import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_DELTA, DATABASE_NAME
from visitegypt.core.authentication.entities.token import TokenPayload, Token
from loguru import logger
from visitegypt.api.container import get_dependencies
from collections import ChainMap
from bson import ObjectId
import uuid
from visitegypt.core.authentication.services.auth_service import create_access_token, create_refresh_token
from visitegypt.infra.database.events import db
from visitegypt.infra.database.utils import users_collection_name
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.accounts.entities.user import UserCreateToken
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from visitegypt.config.environment import MAIL_FROM,MAIL_PASSWORD,MAIL_USERNAME


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

conf = ConnectionConfig(
        MAIL_USERNAME=MAIL_USERNAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM = MAIL_FROM,
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_TLS=True,
        MAIL_SSL=False,
        MAIL_FROM_NAME="Visit Egypt"
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
        user = await repo.check_user_token(token_data.user_id,token_data.token_id)
    except (jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e:
        raise e

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

def get_register_user(token:str) -> UserCreateToken:
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        return payload
    except (jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e:
        raise e

def get_reset_password_user(user_hash:str, token:str) -> UserCreateToken:
    try:
        payload = jwt.decode(token, (str(SECRET_KEY)+user_hash), algorithms=[ALGORITHM])
        return payload
    except (jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e:
        raise e

async def get_refreshed_token(repo:UserRepo,access_token: str,refresh_token:str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tokens are not valid pair",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        access_payload = jwt.decode(access_token, str(SECRET_KEY), algorithms=[ALGORITHM], options={'verify_exp': False})
        refresh_payload = jwt.decode(refresh_token, str(SECRET_KEY), algorithms=[ALGORITHM])
        if access_payload.get("token_id") is None or refresh_payload.get("token_id") is None or access_payload.get("token_id") != refresh_payload.get("token_id"):
            raise credentials_exception
        token_id = str(uuid.uuid1())
        token_data = TokenPayload(**access_payload)
        await repo.update_user_tokenID(user_id=token_data.user_id,old_token_id=token_data.token_id,new_toke_id=token_id)
        token_data.token_id = token_id
        return Token(
            access_token=create_access_token(
                token_data.dict(), expires_delta=JWT_EXPIRATION_DELTA
         ),
            token_type="bearer",
            refresh_token=create_refresh_token(tokent_id=token_id),
            user_id=str(token_data.user_id),
    )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def filters_dict(filters: Optional[List[str]] = Query(None)):
    try:
        return list(map(json.loads, filters))  # If fails, returns JSONDECODEERROR
    except Exception:
        return []


async def common_parameters(
    q: Optional[List] = Depends(filters_dict), page_num: int = 1, limit: int = 10, lang: str = 'en'
):
    dict_of_filters = dict(ChainMap(*q))
    if "_id" not in dict_of_filters and "id" in dict_of_filters:
        dict_of_filters["_id"] = ObjectId(dict_of_filters.pop("id"))
    filter_filters_from_none = {k: v for k, v in dict_of_filters.items() if v}
    return {"filters": filter_filters_from_none, "page_num": page_num, "limit": limit, "lang": lang}

async def send_mail(url:str,email):
    try:

        template = "Hi thanks for registering in Visit Egypt please click on the link below to confirm your account \n"+url
 
        message = MessageSchema(
            subject="Visit Egypt Registration",
            recipients=[email],
            body=template
            )
    
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        raise e

async def send__reset_password_mail(url:str,email):
    try:

        template = "Hi please use the following link to resetyou password \nIf you didn't request password reset please ignore this email \n"+url
 
        message = MessageSchema(
            subject="Visit Egypt Reset Password",
            recipients=[email],
            body=template
            )
    
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        raise e