from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
import math

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import (
    EmployeeCreate, 
    EmployeeUpdate, 
    EmployeeResponse, 
    EmployeeListResponse,
    EmployeeStatus
)
from app.auth import get_password_hash

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee"""
    # Check if email already exists
    db_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    db_employee = db.query(Employee).filter(Employee.username == employee.username).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create employee with hashed password
    employee_data = employee.dict()
    password = employee_data.pop("password")
    hashed_password = get_password_hash(password)
    
    db_employee = Employee(**employee_data, hashed_password=hashed_password)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@router.get("/", response_model=EmployeeListResponse)
def get_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[EmployeeStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all employees with pagination and filtering"""
    query = db.query(Employee)
    
    # Apply filters
    if status:
        query = query.filter(Employee.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Employee.first_name.ilike(search_term)) |
            (Employee.last_name.ilike(search_term)) |
            (Employee.email.ilike(search_term)) |
            (Employee.username.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    employees = query.offset(offset).limit(per_page).all()
    
    return EmployeeListResponse(
        employees=employees,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific employee by ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: UUID,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Update an employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if email is being updated and if it already exists
    if employee_update.email and employee_update.email != employee.email:
        existing_employee = db.query(Employee).filter(
            Employee.email == employee_update.email
        ).first()
        if existing_employee:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username is being updated and if it already exists
    if employee_update.username and employee_update.username != employee.username:
        existing_employee = db.query(Employee).filter(
            Employee.username == employee_update.username
        ).first()
        if existing_employee:
            raise HTTPException(status_code=400, detail="Username already registered")
    
    # Update fields
    update_data = employee_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}")
def deactivate_employee(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate an employee (soft delete)"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.status = EmployeeStatus.INACTIVE
    db.commit()
    
    return {"message": "Employee deactivated successfully"}


@router.post("/{employee_id}/reactivate", response_model=EmployeeResponse, status_code=201)
def reactivate_employee(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Reactivate an inactive employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.status = EmployeeStatus.ACTIVE
    db.commit()
    db.refresh(employee)
    return employee 