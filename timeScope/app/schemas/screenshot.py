from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ScreenshotBase(BaseModel):
    employee_id: str
    time_entry_id: Optional[str] = None
    permission_granted: bool = False
    permission_issue: bool = False


class ScreenshotCreate(ScreenshotBase):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    taken_at: datetime


class ScreenshotUpdate(BaseModel):
    permission_granted: Optional[bool] = None
    permission_issue: Optional[bool] = None


class ScreenshotResponse(ScreenshotBase):
    id: str
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_size_mb: Optional[float] = None
    taken_at: datetime
    created_at: datetime
    has_permission_issues: bool
    
    class Config:
        from_attributes = True


class ScreenshotListResponse(BaseModel):
    screenshots: List[ScreenshotResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ScreenshotUploadResponse(BaseModel):
    id: str
    file_name: str
    file_path: str
    file_size: int
    message: str


class PermissionSummary(BaseModel):
    total_screenshots: int
    permission_granted: int
    permission_issues: int
    employees_with_issues: List[str] 