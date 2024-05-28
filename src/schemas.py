from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


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

    class Config:
        from_attributes = True
