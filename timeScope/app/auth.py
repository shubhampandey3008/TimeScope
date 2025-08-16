from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import UUID
import re

from app.core.config import settings
from app.database import get_db
from app.models.employee import Employee
from app.schemas.auth import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_employee(db: Session, username: str, password: str) -> Optional[Employee]:
    """Authenticate employee with username and password"""
    # Validate input parameters
    if not username or not password:
        return None
    
    # Basic validation to prevent injection attacks
    if len(username) > 100 or len(password) > 200:
        return None
    
    # Check for basic username format
    if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username.strip()):
        return None
    
    try:
        employee = db.query(Employee).filter(Employee.username == username.strip()).first()
        if not employee:
            return None
        
        # Check if employee is active
        if not employee.is_active:
            return None
            
        if not verify_password(password, employee.hashed_password):
            return None
            
        return employee
    except Exception:
        return None


def get_employee_by_username(db: Session, username: str) -> Optional[Employee]:
    """Get employee by username"""
    try:
        return db.query(Employee).filter(Employee.username == username).first()
    except Exception:
        return None


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Basic token format validation
        if not credentials.credentials or len(credentials.credentials) < 20:
            raise invalid_token_exception
        
        # Try to decode the token
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        employee_id: str = payload.get("employee_id")
        exp: int = payload.get("exp")
        
        # Validate required fields
        if username is None or employee_id is None:
            raise invalid_token_exception
        
        # Check if token has expired
        if exp is None or datetime.utcnow().timestamp() > exp:
            raise expired_token_exception
        
        token_data = TokenData(username=username, employee_id=employee_id)
        return token_data
        
    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise invalid_token_exception
    except Exception:
        raise credentials_exception


# Optional: Simple API key authentication for development
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple API key verification for development purposes"""
    # In production, you would want to use proper JWT tokens
    # This is a simplified version for demonstration
    if credentials.credentials != "demo-api-key-123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "demo-user"


def get_current_user(
    token_data: TokenData = Depends(verify_token),
    db: Session = Depends(get_db)
) -> Employee:
    """Get current authenticated user from database"""
    try:
        employee = get_employee_by_username(db, username=token_data.username)
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if employee is still active
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return employee
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional authentication dependency for endpoints that should require auth
def get_current_active_user(current_user: Employee = Depends(get_current_user)) -> Employee:
    """Dependency to get current active user - use this for protected endpoints"""
    return current_user 