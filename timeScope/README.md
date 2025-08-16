# Employee Monitoring API

A comprehensive employee monitoring and time tracking system built with FastAPI, designed to be compatible with Insightful's API patterns. This system provides five core APIs for employee management, project tracking, task management, time tracking, and screenshot monitoring with macOS permission compliance.

## Features

### 🏢 Core APIs

1. **Employee API** - Complete employee lifecycle management
2. **Project API** - Project management with team assignments
3. **Time Tracking API** - Comprehensive time logging and reporting directly on projects
4. **Screenshots API** - Screenshot monitoring with macOS permission flags

**Note**: Time tracking is now directly associated with projects instead of tasks, simplifying the workflow while maintaining all functionality.

### 🔐 Security & Compliance

- JWT-based authentication
- macOS screen recording permission tracking
- CORS middleware configuration
- Environment-based configuration
- Secure file upload handling

### 📊 Database Design

- PostgreSQL primary database support
- SQLite for development/testing
- Proper entity relationships with foreign keys
- Database migrations with Alembic
- UUID primary keys for security

### 🚀 Performance & Scalability

- Pagination for all list endpoints
- Filtering and search capabilities
- Optimized database queries
- Async/await support
- File upload size limits

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- pip or pipenv

### Quick Setup (Recommended)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd employee-monitoring-api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **One-command setup**
   ```bash
   python setup.py
   ```
   This will install dependencies, setup the database, and create your first admin user.

3. **Start the application**
   ```bash
   python run_ui.py
   ```

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-monitoring-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Initialize Alembic
   alembic init alembic
   
   # Generate first migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**

   **Option A: API Only**
   ```bash
   uvicorn app.main:app --reload
   ```

   **Option B: Full UI (Recommended)**
   ```bash
   python run_ui.py
   ```
   This will start both the FastAPI backend (port 8000) and Streamlit UI (port 8501)

## User Interface

### 🎨 Streamlit Web UI

The system includes a comprehensive web interface built with Streamlit:

- **Access**: http://localhost:8501 (when using `python run_ui.py`)
- **Features**: Full CRUD operations for employees and projects
- **Authentication**: Login system with role-based access

#### Admin Features
- **Employee Management**: Create, view, edit, and deactivate employees
- **Project Management**: Full project lifecycle management
- **Project Assignments**: Assign employees to projects with roles

#### User Features
- **Registration**: Self-service account creation
- **Login**: Secure authentication with credentials returned
- **Dashboard**: Personal information and activity overview

### 🔧 Getting Started with the UI

1. **Start the application**:
   ```bash
   python run_ui.py
   ```

2. **Register your first admin user**:
   - Go to http://localhost:8501
   - Click "Register" tab
   - Create a user with position "Admin" or "Manager"

3. **Login and start managing**:
   - Use your credentials to login
   - Admins will see the full management dashboard
   - Regular users will see a simplified interface

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Streamlit UI**: http://localhost:8501

## API Endpoints

### Employee Management

```
POST   /api/v1/employees/              # Create employee
GET    /api/v1/employees/              # List employees (paginated)
GET    /api/v1/employees/{id}          # Get employee
PUT    /api/v1/employees/{id}          # Update employee
DELETE /api/v1/employees/{id}          # Deactivate employee
POST   /api/v1/employees/{id}/reactivate # Reactivate employee
```

### Project Management

```
POST   /api/v1/projects/               # Create project
GET    /api/v1/projects/               # List projects (paginated)
GET    /api/v1/projects/{id}           # Get project
PUT    /api/v1/projects/{id}           # Update project
DELETE /api/v1/projects/{id}           # Delete project
POST   /api/v1/projects/{id}/employees # Assign employee to project
DELETE /api/v1/projects/{id}/employees/{employee_id} # Remove employee
GET    /api/v1/projects/{id}/employees # List project employees
```



### Time Tracking

```
POST   /api/v1/time-tracking/          # Create time entry
GET    /api/v1/time-tracking/          # List time entries (paginated)
GET    /api/v1/time-tracking/{id}      # Get time entry
PUT    /api/v1/time-tracking/{id}      # Update time entry
DELETE /api/v1/time-tracking/{id}      # Delete time entry
POST   /api/v1/time-tracking/start     # Start time tracking
POST   /api/v1/time-tracking/stop      # Stop time tracking
GET    /api/v1/time-tracking/active/{employee_id} # Get active time entry
GET    /api/v1/time-tracking/summary/employees    # Employee time summaries
```

### Screenshot Management

```
POST   /api/v1/screenshots/upload      # Upload screenshot file
POST   /api/v1/screenshots/            # Create screenshot record
GET    /api/v1/screenshots/            # List screenshots (paginated)
GET    /api/v1/screenshots/{id}        # Get screenshot
PUT    /api/v1/screenshots/{id}        # Update screenshot (permissions)
DELETE /api/v1/screenshots/{id}        # Delete screenshot
GET    /api/v1/screenshots/permissions/summary # Permission summary
GET    /api/v1/screenshots/employee/{id}/permissions # Employee permissions
```

## Database Schema

### Core Entities

- **Employee**: User management with status tracking
- **Project**: Project management with date ranges
- **TimeEntry**: Time tracking with duration calculation
- **Screenshot**: File management with permission flags

### Relationships

- Many-to-many: Projects ↔ Employees
- One-to-many: Employees → TimeEntries
- One-to-many: Projects → TimeEntries
- One-to-many: TimeEntries → Screenshots

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/employee_monitoring
SQLITE_DATABASE_URL=sqlite:///./employee_monitoring.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["png", "jpg", "jpeg", "gif"]

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=your-bucket
```

## Key Features Explained

### 1. Employee Management
- Full CRUD operations with soft delete (deactivation)
- Email uniqueness validation
- Status tracking (active, inactive, suspended)
- Reactivation capability

### 2. Project Management
- Project lifecycle management
- Employee assignments with roles
- Status tracking with multiple states
- Team collaboration features

### 3. Time Tracking
- Start/stop time tracking
- Duration calculation
- Employee time summaries
- Date range filtering
- Active time entry management

### 5. Screenshot Management
- **macOS Permission Compliance**: Critical for screen recording permissions
- File upload with validation
- Permission flag tracking
- Employee-specific organization
- Permission issue monitoring

## macOS Permission Handling

The screenshots API includes special handling for macOS screen recording permissions:

- `permission_granted`: Boolean flag for permission status
- `permission_issue`: Boolean flag for permission problems
- Permission summary endpoints for monitoring compliance
- Employee-specific permission tracking

This is crucial for macOS deployments where screen recording requires explicit user permission.

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Structure

```
app/
├── api/                # FastAPI route handlers
├── core/               # Configuration and utilities
├── models/             # SQLAlchemy database models
├── schemas/            # Pydantic validation schemas
├── database.py         # Database connection
└── main.py            # FastAPI application
```

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

1. Set up PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Set up file storage (local or S3)
5. Configure reverse proxy (nginx)
6. Set up SSL certificates

## Security Considerations

- Change default SECRET_KEY in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates
- Database connection pooling
- File upload validation

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the database schema
- Check environment configuration
- Verify file permissions for uploads

---

Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL 