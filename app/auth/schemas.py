from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    password2: Optional[str] = None

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    external_id: Optional[UUID4] = None
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
