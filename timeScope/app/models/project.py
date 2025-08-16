from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid
import enum


class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee_assignments = relationship("ProjectEmployee", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
    
    @property
    def is_active(self):
        return self.status == ProjectStatus.ACTIVE 