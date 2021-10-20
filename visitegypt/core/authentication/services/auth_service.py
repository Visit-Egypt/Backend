from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from visitegypt.config.environment import SECRET_KEY, ALGORITHM, JWT_EXPIRATION_DELTA
from visitegypt.core.accounts.protocols.user_repo import UserRepo
from visitegypt.core.authentication.entities.userauth import UserAuthBody
from visitegypt.core.authentication.entities.token import Token, TokenPayload
from visitegypt.core.errors.user_errors import WrongEmailOrPassword
from visitegypt.core.accounts.services.hash_service import verify_password

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
        expire = datetime.utcnow() + timedelta(minutes=15)
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

    token_payload = TokenPayload(user_id=str(user_to_auth.id), role=role)

    return Token(
        access_token=create_access_token(
            token_payload.dict(), expires_delta=JWT_EXPIRATION_DELTA
        ),
        token_type="bearer",
        user_id=str(user_to_auth.id),
    )
