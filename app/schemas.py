from pydantic import BaseModel
from pydantic.networks import EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut (BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class UserLogin (BaseModel):
    email: EmailStr
    password: str

class UserEmail (BaseModel):
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
   #rating: Optional[int] = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserEmail

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)