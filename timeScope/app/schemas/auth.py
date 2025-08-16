from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: UUID
    username: str
    full_name: str
    email: str
    position: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None
    employee_id: Optional[UUID] = None 