from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TimeEntryBase(BaseModel):
    employee_id: str
    project_id: str
    description: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    start_time: datetime


class TimeEntryUpdate(BaseModel):
    end_time: Optional[datetime] = None
    description: Optional[str] = None


class TimeEntryResponse(TimeEntryBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    duration_minutes: Optional[float] = None
    duration_hours: Optional[float] = None
    app_usage_data: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TimeEntryListResponse(BaseModel):
    time_entries: List[TimeEntryResponse]
    total: int
    page: int
    per_page: int
    pages: int


class TimeEntryStart(BaseModel):
    project_id: str
    description: Optional[str] = None


class TimeEntryStop(BaseModel):
    description: Optional[str] = None
    app_usage_data: Optional[List[str]] = None


class EmployeeTimeSummary(BaseModel):
    employee_id: str
    employee_name: str
    total_duration_seconds: int
    total_duration_hours: float
    total_entries: int
    date_range: str 