import os
import json
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

import aiofiles
from pathlib import Path
import uuid
import math

from app.database import get_db
from app.models.screenshot import Screenshot
from app.models.employee import Employee
from app.models.time_entry import TimeEntry
from app.schemas.screenshot import (
    ScreenshotCreate, 
    ScreenshotUpdate, 
    ScreenshotResponse, 
    ScreenshotListResponse,
    ScreenshotUploadResponse,
    PermissionSummary
)
from app.core.config import settings
from sqlalchemy import func

router = APIRouter(prefix="/screenshots", tags=["screenshots"])


def save_uploaded_file(file: UploadFile, employee_id: str) -> tuple[str, str, int]:
    """Save uploaded file and return file path, file name, and file size"""
    # Create employee-specific directory
    employee_dir = Path(settings.UPLOAD_DIR) / employee_id
    employee_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = employee_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return str(file_path), unique_filename, len(content)


@router.post("/", response_model=ScreenshotResponse, status_code=201)
def create_screenshot(
    screenshot: ScreenshotCreate,
    db: Session = Depends(get_db)
):
    """Create a new screenshot record"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == screenshot.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if time entry exists (if provided)
    if screenshot.time_entry_id:
        time_entry = db.query(TimeEntry).filter(TimeEntry.id == screenshot.time_entry_id).first()
        if not time_entry:
            raise HTTPException(status_code=404, detail="Time entry not found")
    
    db_screenshot = Screenshot(**screenshot.dict())
    db.add(db_screenshot)
    db.commit()
    db.refresh(db_screenshot)
    return db_screenshot


@router.post("/upload", response_model=ScreenshotUploadResponse, status_code=201)
async def upload_screenshot(
    employee_id: str = Form(...),
    time_entry_id: Optional[str] = Form(None),
    permission_granted: bool = Form(False),
    permission_issue: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a screenshot file"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if time entry exists (if provided)
    if time_entry_id:
        time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
        if not time_entry:
            raise HTTPException(status_code=404, detail="Time entry not found")
    
    # Validate file type
    if not file.filename.lower().endswith(tuple(f".{ext}" for ext in settings.ALLOWED_EXTENSIONS)):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Save file
    try:
        file_path, file_name, file_size = save_uploaded_file(file, employee_id)
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            os.remove(file_path)  # Clean up
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Create screenshot record
        db_screenshot = Screenshot(
            employee_id=employee_id,
            time_entry_id=time_entry_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            permission_granted=permission_granted,
            permission_issue=permission_issue,
            taken_at=datetime.utcnow()
        )
        db.add(db_screenshot)
        db.commit()
        db.refresh(db_screenshot)
        
        return ScreenshotUploadResponse(
            id=str(db_screenshot.id),
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            message="Screenshot uploaded successfully"
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to upload screenshot: {str(e)}")


@router.get("/", response_model=ScreenshotListResponse)
def get_screenshots(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    employee_id: Optional[str] = None,
    time_entry_id: Optional[str] = None,
    permission_granted: Optional[bool] = None,
    permission_issue: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get all screenshots with pagination and filtering"""
    query = db.query(Screenshot)
    
    # Apply filters
    if employee_id:
        query = query.filter(Screenshot.employee_id == employee_id)
    
    if time_entry_id:
        query = query.filter(Screenshot.time_entry_id == time_entry_id)
    
    if permission_granted is not None:
        query = query.filter(Screenshot.permission_granted == permission_granted)
    
    if permission_issue is not None:
        query = query.filter(Screenshot.permission_issue == permission_issue)
    
    if start_date:
        query = query.filter(Screenshot.taken_at >= start_date)
    
    if end_date:
        query = query.filter(Screenshot.taken_at <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    screenshots = query.offset(offset).limit(per_page).all()
    
    return ScreenshotListResponse(
        screenshots=screenshots,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )


@router.get("/{screenshot_id}", response_model=ScreenshotResponse)
def get_screenshot(
    screenshot_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific screenshot by ID"""
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return screenshot


@router.put("/{screenshot_id}", response_model=ScreenshotResponse)
def update_screenshot(
    screenshot_id: str,
    screenshot_update: ScreenshotUpdate,
    db: Session = Depends(get_db)
):
    """Update a screenshot (mainly for permission flags)"""
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    # Update fields
    for field, value in screenshot_update.dict(exclude_unset=True).items():
        setattr(screenshot, field, value)
    
    db.commit()
    db.refresh(screenshot)
    return screenshot


@router.delete("/{screenshot_id}")
def delete_screenshot(
    screenshot_id: str,
    db: Session = Depends(get_db)
):
    """Delete a screenshot and its file"""
    screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not screenshot:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    
    # Delete file if it exists
    if screenshot.file_path and os.path.exists(screenshot.file_path):
        try:
            os.remove(screenshot.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {screenshot.file_path}: {e}")
    
    db.delete(screenshot)
    db.commit()
    
    return {"message": "Screenshot deleted successfully"}


@router.get("/permissions/summary", response_model=PermissionSummary)
def get_permission_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get summary of screenshot permissions"""
    query = db.query(Screenshot)
    
    # Apply date filters
    if start_date:
        query = query.filter(Screenshot.taken_at >= start_date)
    if end_date:
        query = query.filter(Screenshot.taken_at <= end_date)
    
    total_screenshots = query.count()
    permission_granted = query.filter(Screenshot.permission_granted == True).count()
    permission_issues = query.filter(Screenshot.permission_issue == True).count()
    
    # Get employees with permission issues
    employees_with_issues = db.query(Employee.id, Employee.first_name, Employee.last_name)\
        .join(Screenshot)\
        .filter(Screenshot.permission_issue == True)\
        .distinct()\
        .all()
    
    return PermissionSummary(
        total_screenshots=total_screenshots,
        permission_granted=permission_granted,
        permission_issues=permission_issues,
        employees_with_issues=[
            f"{emp.first_name} {emp.last_name} ({emp.id})" 
            for emp in employees_with_issues
        ]
    )


@router.get("/employee/{employee_id}/permissions")
def get_employee_permission_status(employee_id: str, db: Session = Depends(get_db)):
    """Get permission status for a specific employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get latest screenshot for permission status
    latest_screenshot = db.query(Screenshot)\
        .filter(Screenshot.employee_id == employee_id)\
        .order_by(Screenshot.taken_at.desc())\
        .first()
    
    if not latest_screenshot:
        return {
            "employee_id": employee_id,
            "has_screenshots": False,
            "permission_granted": None,
            "permission_issue": None,
            "last_screenshot_at": None
        }
    
    return {
        "employee_id": employee_id,
        "has_screenshots": True,
        "permission_granted": latest_screenshot.permission_granted,
        "permission_issue": latest_screenshot.permission_issue,
        "last_screenshot_at": latest_screenshot.taken_at
    } 