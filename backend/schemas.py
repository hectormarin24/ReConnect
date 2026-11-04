from typing import Optional, List

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


class ContactCreate(BaseModel):
    fname: str
    lname: Optional[str] = None
    mname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    tags: List[str] = []


class ContactUpdate(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    mname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    tags: Optional[List[str]] = None

class ContactAddRequest(BaseModel):
    fname: str
    lname: Optional[str] = None
    mname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    tags: List[str] = []

class ContactUpdateRequest(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    mname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class ContactDeleteRequest(BaseModel):
    id: int
