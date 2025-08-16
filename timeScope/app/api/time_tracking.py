from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date


from app.database import get_db
from app.models.time_entry import TimeEntry
from app.models.employee import Employee
from app.models.project import Project
from app.schemas.time_entry import (
    TimeEntryCreate, 
    TimeEntryUpdate, 
    TimeEntryResponse, 
    TimeEntryListResponse,
    TimeEntryStart,
    TimeEntryStop,
    EmployeeTimeSummary
)
from sqlalchemy import func, and_
import math

router = APIRouter(prefix="/time-tracking", tags=["time-tracking"])


@router.post("/", response_model=TimeEntryResponse, status_code=201)
def create_time_entry(
    time_entry: TimeEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new time entry"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == time_entry.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == time_entry.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_time_entry = TimeEntry(**time_entry.dict())
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


@router.get("/", response_model=TimeEntryListResponse)
def get_time_entries(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    employee_id: Optional[str] = None,
    project_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all time entries with pagination and filtering"""
    query = db.query(TimeEntry)
    
    # Apply filters
    if employee_id:
        query = query.filter(TimeEntry.employee_id == employee_id)
    
    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    
    if end_date:
        query = query.filter(TimeEntry.start_time <= end_date)
    
    if is_active is not None:
        query = query.filter(TimeEntry.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    time_entries = query.offset(offset).limit(per_page).all()
    
    return TimeEntryListResponse(
        time_entries=time_entries,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )


@router.get("/{time_entry_id}", response_model=TimeEntryResponse)
def get_time_entry(
    time_entry_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific time entry by ID"""
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return time_entry


@router.put("/{time_entry_id}", response_model=TimeEntryResponse)
def update_time_entry(
    time_entry_id: str,
    time_entry_update: TimeEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a time entry"""
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    # Update fields
    for field, value in time_entry_update.dict(exclude_unset=True).items():
        setattr(time_entry, field, value)
    
    # Calculate duration if end_time is provided
    if time_entry.end_time and time_entry.start_time:
        duration = time_entry.end_time - time_entry.start_time
        time_entry.duration_seconds = int(duration.total_seconds())
        time_entry.is_active = False
    
    db.commit()
    db.refresh(time_entry)
    return time_entry


@router.delete("/{time_entry_id}")
def delete_time_entry(
    time_entry_id: str,
    db: Session = Depends(get_db)
):
    """Delete a time entry"""
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == time_entry_id).first()
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    db.delete(time_entry)
    db.commit()
    
    return {"message": "Time entry deleted successfully"}


@router.post("/start", response_model=TimeEntryResponse, status_code=201)
def start_time_tracking(
    employee_id: str,
    time_entry_start: TimeEntryStart,
    db: Session = Depends(get_db)
):
    """Start time tracking for an employee"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == time_entry_start.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if employee has any active time entries
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.employee_id == employee_id,
        TimeEntry.is_active == True
    ).first()
    
    if active_entry:
        raise HTTPException(status_code=400, detail="Employee already has an active time entry")
    
    # Create new time entry
    db_time_entry = TimeEntry(
        employee_id=employee_id,
        project_id=time_entry_start.project_id,
        start_time=datetime.utcnow(),
        description=time_entry_start.description,
        is_active=True
    )
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    
    return db_time_entry


@router.post("/stop", response_model=TimeEntryResponse)
def stop_time_tracking(
    employee_id: str,
    time_entry_stop: TimeEntryStop,
    db: Session = Depends(get_db)
):
    """Stop time tracking for an employee"""
    # Find active time entry for employee
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.employee_id == employee_id,
        TimeEntry.is_active == True
    ).first()
    
    if not active_entry:
        raise HTTPException(status_code=404, detail="No active time entry found for employee")
    
    # Update time entry
    active_entry.end_time = datetime.utcnow()
    active_entry.is_active = False
    
    # Calculate duration
    duration = active_entry.end_time - active_entry.start_time
    active_entry.duration_seconds = int(duration.total_seconds())
    
    if time_entry_stop.description:
        active_entry.description = time_entry_stop.description
    
    # Store app usage data as JSON
    if time_entry_stop.app_usage_data:
        active_entry.app_usage_data = time_entry_stop.app_usage_data
    
    db.commit()
    db.refresh(active_entry)
    
    return active_entry


@router.get("/active/{employee_id}", response_model=Optional[TimeEntryResponse])
def get_active_time_entry(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """Get active time entry for an employee"""
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.employee_id == employee_id,
        TimeEntry.is_active == True
    ).first()
    
    return active_entry


@router.get("/summary/employees", response_model=List[EmployeeTimeSummary])
def get_employee_time_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get time summary for all employees"""
    query = db.query(
        Employee.id,
        Employee.first_name,
        Employee.last_name,
        func.sum(TimeEntry.duration_seconds).label('total_duration'),
        func.count(TimeEntry.id).label('total_entries')
    ).join(TimeEntry).filter(TimeEntry.duration_seconds.isnot(None))
    
    # Apply date filters
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.start_time <= end_date)
    
    query = query.group_by(Employee.id, Employee.first_name, Employee.last_name)
    results = query.all()
    
    date_range = f"{start_date or 'Beginning'} to {end_date or 'Present'}"
    
    return [
        EmployeeTimeSummary(
            employee_id=str(result.id),
            employee_name=f"{result.first_name} {result.last_name}",
            total_duration_seconds=result.total_duration or 0,
            total_duration_hours=(result.total_duration or 0) / 3600,
            total_entries=result.total_entries or 0,
            date_range=date_range
        )
        for result in results
    ] 