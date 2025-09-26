from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class RoleRead(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Optional[RoleRead] = None
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class PostCreate(BaseModel):
    title: str
    content: str

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author: UserRead
    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: Optional[UserRead] = None
    class Config:
        orm_mode = True
