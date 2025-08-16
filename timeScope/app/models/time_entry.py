from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(GUID(), ForeignKey("employees.id"), nullable=False)
    project_id = Column(GUID(), ForeignKey("projects.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    app_usage_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    screenshots = relationship("Screenshot", back_populates="time_entry")
    
    @property
    def duration_minutes(self):
        if self.duration_seconds:
            return self.duration_seconds / 60
        return None
    
    @property
    def duration_hours(self):
        if self.duration_seconds:
            return self.duration_seconds / 3600
        return None 