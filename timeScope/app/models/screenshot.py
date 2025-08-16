from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid

class Screenshot(Base):
    __tablename__ = "screenshots"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    employee_id = Column(GUID(), ForeignKey("employees.id"), nullable=False)
    time_entry_id = Column(GUID(), ForeignKey("time_entries.id"), nullable=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    permission_granted = Column(Boolean, default=False)
    permission_issue = Column(Boolean, default=False)
    taken_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="screenshots")
    time_entry = relationship("TimeEntry", back_populates="screenshots")
    
    @property
    def file_size_mb(self):
        if self.file_size:
            return self.file_size / (1024 * 1024)
        return None
    
    @property
    def has_permission_issues(self):
        return self.permission_issue or not self.permission_granted 