from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid


class ProjectEmployee(Base):
    __tablename__ = "project_employees"
    
    project_id = Column(GUID(), ForeignKey("projects.id"), primary_key=True)
    employee_id = Column(GUID(), ForeignKey("employees.id"), primary_key=True)
    role = Column(String, default="member")  # member, lead, manager
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="employee_assignments")
    employee = relationship("Employee", back_populates="project_assignments") 