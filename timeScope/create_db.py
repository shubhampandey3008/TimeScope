#!/usr/bin/env python3
"""
Create database with correct schema
"""

from app.database import engine
from app.models import Base
from app.models.employee import Employee, EmployeeStatus
from app.models.project import Project, ProjectStatus
from app.auth import get_password_hash
from sqlalchemy.orm import sessionmaker

def create_database():
    """Create all tables and add default admin user"""
    print("🔄 Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(Employee).filter(Employee.email == "admin@company.com").first()
        
        if not admin_user:
            print("🔄 Creating default admin user...")
            # Create default admin user
            admin_user = Employee(
                email="admin@company.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                first_name="System",
                last_name="Administrator",
                phone="+1-555-0000",
                position="Administrator",
                status=EmployeeStatus.ACTIVE
            )
            db.add(admin_user)
            
            # Create some sample projects
            sample_projects = [
                Project(
                    name="Website Redesign",
                    description="Complete redesign of company website",
                    status=ProjectStatus.ACTIVE
                ),
                Project(
                    name="Mobile App Development",
                    description="Develop mobile application for iOS and Android",
                    status=ProjectStatus.ACTIVE
                ),
                Project(
                    name="Data Migration",
                    description="Migrate legacy data to new system",
                    status=ProjectStatus.COMPLETED
                ),
                Project(
                    name="Security Audit",
                    description="Comprehensive security audit of all systems",
                    status=ProjectStatus.ON_HOLD
                ),
                Project(
                    name="Performance Optimization",
                    description="Optimize application performance",
                    status=ProjectStatus.INACTIVE
                )
            ]
            
            for project in sample_projects:
                db.add(project)
            
            db.commit()
            print("✅ Default admin user created!")
            print("📧 Email: admin@company.com")
            print("🔑 Password: admin123")
            print("✅ Sample projects created!")
        else:
            print("ℹ️ Admin user already exists")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏢 Creating Employee Monitoring Database...")
    create_database()
    print("🎉 Database setup completed!") 