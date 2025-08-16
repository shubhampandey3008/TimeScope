from sqlalchemy import Column, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid
import enum


class EmployeeStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    position = Column(String, nullable=True)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    time_entries = relationship("TimeEntry", back_populates="employee")
    screenshots = relationship("Screenshot", back_populates="employee")
    project_assignments = relationship("ProjectEmployee", back_populates="employee")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self):
        return self.status == EmployeeStatus.ACTIVE 