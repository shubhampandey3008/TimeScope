from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class EmployeeBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and v.strip():
            # Basic phone number validation - accepts various formats
            phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{8,}[\d]$'
            if not re.match(phone_pattern, v.strip()):
                raise ValueError('Phone number must be a valid format (minimum 9 digits)')
        return v.strip() if v else None

    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_\-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        v = v.strip()
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, apostrophes, and periods')
        return v

class EmployeeCreate(EmployeeBase):
    password: str = Field(..., min_length=8, max_length=128)

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        
        # Check for at least one uppercase, one lowercase, and one number
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        return v

class EmployeeUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)
    status: Optional[EmployeeStatus] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and v.strip():
            phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{8,}[\d]$'
            if not re.match(phone_pattern, v.strip()):
                raise ValueError('Phone number must be a valid format (minimum 9 digits)')
        return v.strip() if v else None

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Username cannot be empty')
            v = v.strip()
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not re.match(r'^[a-zA-Z0-9_\-]+$', v):
                raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            v = v.strip()
            if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
                raise ValueError('Name can only contain letters, spaces, hyphens, apostrophes, and periods')
        return v

class EmployeeResponse(EmployeeBase):
    id: str
    status: EmployeeStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    per_page: int
    pages: int 