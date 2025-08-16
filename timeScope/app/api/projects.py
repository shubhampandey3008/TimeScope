from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import ValidationError

from sqlalchemy import func
import math

from app.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.employee import Employee
from app.models.associations import ProjectEmployee
from app.schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectListResponse,
    ProjectEmployeeAssignment,
    ProjectEmployeeResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project"""
    try:
        # Additional validation for dates
        if project.start_date and project.end_date:
            if project.end_date <= project.start_date:
                raise HTTPException(status_code=422, detail="End date must be after start date")
        
        # Check for duplicate project names
        existing_project = db.query(Project).filter(Project.name == project.name).first()
        if existing_project:
            raise HTTPException(status_code=422, detail="Project with this name already exists")
        
        db_project = Project(**project.dict())
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if "422" in str(e):
            raise e
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=ProjectListResponse)
def get_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all projects with pagination and filtering"""
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be greater than 0")
    if per_page < 1 or per_page > 100:
        raise HTTPException(status_code=422, detail="Per page must be between 1 and 100")
    
    query = db.query(Project)
    
    # Apply filters
    if status:
        query = query.filter(Project.status == status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Project.name.ilike(search_term)) |
            (Project.description.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    projects = query.offset(offset).limit(per_page).all()
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page)
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check for duplicate project names (if name is being updated)
        if project_update.name and project_update.name != project.name:
            existing_project = db.query(Project).filter(Project.name == project_update.name).first()
            if existing_project:
                raise HTTPException(status_code=422, detail="Project with this name already exists")
        
        # Additional date validation for updates
        start_date = project_update.start_date if project_update.start_date is not None else project.start_date
        end_date = project_update.end_date if project_update.end_date is not None else project.end_date
        
        if start_date and end_date and end_date <= start_date:
            raise HTTPException(status_code=422, detail="End date must be after start date")
        
        # Update fields
        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        return project
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if "422" in str(e):
            raise e
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete (deactivate) a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.status = ProjectStatus.INACTIVE
    db.commit()
    
    return {"message": "Project deactivated successfully"}


@router.post("/{project_id}/employees", response_model=ProjectEmployeeResponse, status_code=201)
def assign_employee_to_project(
    project_id: UUID,
    assignment: ProjectEmployeeAssignment,
    db: Session = Depends(get_db)
):
    """Assign an employee to a project"""
    try:
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if employee exists
        employee = db.query(Employee).filter(Employee.id == assignment.employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if assignment already exists
        existing_assignment = db.query(ProjectEmployee).filter(
            ProjectEmployee.project_id == project_id,
            ProjectEmployee.employee_id == assignment.employee_id
        ).first()
        
        if existing_assignment:
            raise HTTPException(status_code=422, detail="Employee already assigned to this project")
        
        # Create assignment
        db_assignment = ProjectEmployee(
            project_id=project_id,
            employee_id=assignment.employee_id,
            role=assignment.role
        )
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        
        return db_assignment
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if "422" in str(e):
            raise e
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}/employees", response_model=List[ProjectEmployeeResponse])
def get_project_employees(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all employees assigned to a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    assignments = db.query(ProjectEmployee).filter(
        ProjectEmployee.project_id == project_id
    ).all()
    
    return assignments


@router.delete("/{project_id}/employees/{employee_id}")
def remove_employee_from_project(
    project_id: UUID,
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove an employee from a project"""
    assignment = db.query(ProjectEmployee).filter(
        ProjectEmployee.project_id == project_id,
        ProjectEmployee.employee_id == employee_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Employee assignment not found")
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Employee removed from project successfully"} 