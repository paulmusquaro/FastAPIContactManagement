from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=5, max_length=50)
    email: EmailStr
    phonenumber: str = Field(min_length=12, max_length=15)
    birthdate: Optional[date] = None
    additional_info: Optional[str] = None


class ContactUpdate(ContactSchema):
    birthdate: date
    additional_info: str


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phonenumber: str
    birthdate: Optional[date] = None
    additional_info: Optional[str] = None
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr