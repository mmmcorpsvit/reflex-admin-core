# Example Pydantic schemas for the demo models
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    active: bool = True

class UserUpdate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    active: bool

class PostCreate(BaseModel):
    title: str
    body: str
    user_id: int
    published: bool = False

class PostUpdate(BaseModel):
    title: str
    body: str
    published: bool
