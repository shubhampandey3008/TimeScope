from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.database import engine, Base
from app.api import employees, projects, time_tracking, screenshots, auth

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Employee Monitoring API",
    description="A comprehensive employee monitoring and time tracking system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

# Mount static files for screenshots
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(employees.router, prefix="/api/v1", tags=["employees"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(time_tracking.router, prefix="/api/v1", tags=["time-tracking"])
app.include_router(screenshots.router, prefix="/api/v1", tags=["screenshots"])

@app.get("/")
async def root():
    return {"message": "Employee Monitoring API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 