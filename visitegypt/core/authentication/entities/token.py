from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    user_id: str


class TokenPayload(BaseModel):
    user_id: str
    role: str
    token_id: str

class RefreshRequest(BaseModel):
    access_token: str
    refresh_token: str