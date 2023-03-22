# Pydantic user schema for database and API

from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    external_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass
