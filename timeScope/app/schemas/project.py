from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

from enum import Enum
from app.models.project import ProjectStatus


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Project name must be at least 1 character long')
        # Allow alphanumeric, spaces, hyphens, underscores, dots, and parentheses
        if not re.match(r'^[a-zA-Z0-9\s\-_\.\(\)]+$', v):
            raise ValueError('Project name contains invalid characters')
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip() if v else None
            if v and len(v) > 1000:
                raise ValueError('Description cannot exceed 1000 characters')
        return v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        if v is not None:
            # Don't allow dates too far in the past (more than 10 years)
            from datetime import timezone
            now = datetime.now(timezone.utc)
            min_date = now.replace(year=now.year - 10)
            
            # Handle timezone-aware vs timezone-naive comparison
            if v.tzinfo is None:
                # Input is timezone-naive, compare with naive datetime
                min_date = min_date.replace(tzinfo=None)
                now = now.replace(tzinfo=None)
            
            if v < min_date:
                raise ValueError('Start date cannot be more than 10 years in the past')
        return v


class ProjectCreate(ProjectBase):
    @validator('end_date')
    def validate_create_dates(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Project name cannot be empty')
            v = v.strip()
            if len(v) < 1:
                raise ValueError('Project name must be at least 1 character long')
            if not re.match(r'^[a-zA-Z0-9\s\-_\.\(\)]+$', v):
                raise ValueError('Project name contains invalid characters')
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip() if v else None
            if v and len(v) > 1000:
                raise ValueError('Description cannot exceed 1000 characters')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        if v is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            min_date = now.replace(year=now.year - 10)
            
            # Handle timezone-aware vs timezone-naive comparison
            if v.tzinfo is None:
                # Input is timezone-naive, compare with naive datetime
                min_date = min_date.replace(tzinfo=None)
                now = now.replace(tzinfo=None)
            
            if v < min_date:
                raise ValueError('Start date cannot be more than 10 years in the past')
        return v


class ProjectResponse(ProjectBase):
    id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectEmployeeAssignment(BaseModel):
    employee_id: str
    role: str = Field(default="member")

    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID cannot be empty')
        return v.strip()

    @validator('role')
    def validate_role(cls, v):
        if v not in ['member', 'lead', 'manager']:
            raise ValueError('Role must be one of: member, lead, manager')
        return v


class ProjectEmployeeResponse(BaseModel):
    employee_id: str
    role: str
    assigned_at: datetime
    
    class Config:
        from_attributes = True 