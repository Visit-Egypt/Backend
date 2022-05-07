from datetime import datetime, timedelta
from re import U
from typing import Optional
from jose import jwt
from pydantic import ValidationError
from visitegypt.config.environment import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_DELTA,JWT_REFRESH_EXPIRATION_DELTA
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.authentication.entities.userauth import UserAuthBody,UserGoogleAuthBody
from visitegypt.core.authentication.entities.token import Token, TokenPayload
from visitegypt.core.errors.user_errors import WrongEmailOrPassword,UserNotFoundError
from visitegypt.core.accounts.services.hash_service import verify_password
import uuid
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from visitegypt.core.accounts.entities.user import UserCreateToken

CLIENT_ID = "1008372786382-b12co7cdm09mssi73ip89bdmtt66294i.apps.googleusercontent.com"

"""
def create_access_token(
    subject: Optional[Dict[str, str]], expires_mins: int = None
) -> str:
    current_time = int(time.time())
    if expires_mins:
        expire = current_time + expires_mins
    else:
        expire = current_time + ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode = {"exp": expire, **subject}
    encoded_jwt = jwt.encode(
        to_encode, str(SECRET_KEY), algorithm=ALGORITHM
    )
    return encoded_jwt
"""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    return encoded_jwt


async def login_access_token(repo: UserRepo, user: UserAuthBody) -> Token:
    user_to_auth = await repo.get_user_by_email(user.email)
    if not user_to_auth:
        raise WrongEmailOrPassword
    user_hash = await repo.get_user_hashed_password(user_to_auth.id)

    if not verify_password(user.password, user_hash):
        raise WrongEmailOrPassword

    if not user_to_auth.user_role:
        role = "USER"
    else:
        role = user_to_auth.user_role
    token_id = str(uuid.uuid1())
    await repo.update_user_tokenID(user_id=user_to_auth.id,new_toke_id=token_id)
    token_payload = TokenPayload(user_id=str(user_to_auth.id), role=role,token_id=token_id)

    return Token(
        access_token=create_access_token(
            token_payload.dict(), expires_delta=JWT_EXPIRATION_DELTA
        ),
        token_type="bearer",
        refresh_token=create_refresh_token(tokent_id=token_id),
        user_id=str(user_to_auth.id),
    )

def register_access_token(repo: UserRepo, user):
    access_token = create_access_token(
            user, expires_delta=JWT_EXPIRATION_DELTA
        )
    return access_token

async def login_google_access_token(repo: UserRepo, token: UserGoogleAuthBody) -> Token:
    try:
        user = id_token.verify_oauth2_token(token.token, requests.Request(), CLIENT_ID)
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user_to_auth = await repo.get_user_by_email(user["email"])
    if not user_to_auth:
        raise UserNotFoundError

    if not user_to_auth.user_role:
        role = "USER"
    else:
        role = user_to_auth.user_role
    token_id = str(uuid.uuid1())
    await repo.update_user_tokenID(user_id=user_to_auth.id,new_toke_id=token_id)
    token_payload = TokenPayload(user_id=str(user_to_auth.id), role=role,token_id=token_id)

    return Token(
        access_token=create_access_token(
            token_payload.dict(), expires_delta=JWT_EXPIRATION_DELTA
        ),
        token_type="bearer",
        refresh_token=create_refresh_token(tokent_id=token_id),
        user_id=str(user_to_auth.id),
    )

def create_refresh_token(tokent_id:str):
    to_encode = {"token_id":tokent_id}
    expire = datetime.utcnow() + JWT_REFRESH_EXPIRATION_DELTA
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    return encoded_jwt