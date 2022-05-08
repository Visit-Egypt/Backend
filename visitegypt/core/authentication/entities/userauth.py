from pydantic import BaseModel, EmailStr


class UserAuthBody(BaseModel):
    email: EmailStr
    password: str


class UserGoogleAuthBody(BaseModel):
    token:str

class UserPasswordReset(BaseModel):
    password:str