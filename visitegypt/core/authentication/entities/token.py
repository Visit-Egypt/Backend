from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    user_id: str


class TokenPayload(BaseModel):
    user_id: str
    role: str
