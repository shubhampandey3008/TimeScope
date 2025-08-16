from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import ValidationError

from app.database import get_db
from app.auth import authenticate_employee, create_access_token
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate employee and return access token"""
    try:
        # Validate input data
        if not login_data.username or not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username and password are required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Strip whitespace
        username = login_data.username.strip()
        password = login_data.password
        
        # Additional validation
        if len(username) < 3 or len(username) > 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username must be between 3 and 50 characters",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 6 characters",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Authenticate employee
        employee = authenticate_employee(db, username, password)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if employee is active
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee account is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": employee.username, "employee_id": str(employee.id)},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            employee_id=employee.id,
            username=employee.username,
            full_name=employee.full_name,
            email=employee.email,
            position=employee.position
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception:
        # Catch any other errors and return a generic auth failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) 