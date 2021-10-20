from pydantic import BaseModel, EmailStr


class UserAuthBody(BaseModel):
    email: EmailStr
    password: str
