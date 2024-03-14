from pydantic import BaseModel, EmailStr
from datetime import datetime 
from typing import Optional


# creating class and testing fields in same time
# testing existance and type of fiels  
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attribute = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_model = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token  : str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

