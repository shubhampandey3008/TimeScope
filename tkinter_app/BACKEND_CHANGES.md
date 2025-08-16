# Backend Changes for App Usage Data

## Required Changes to Support App Usage Data in Stop Time Tracking

### 1. Update TimeEntryStop Schema

You need to update your `TimeEntryStop` schema to accept the app usage data. Add a new field:

```python
# In your schemas/time_entry.py or equivalent
from typing import List, Optional
from pydantic import BaseModel

class TimeEntryStop(BaseModel):
    description: Optional[str] = None
    app_usage_data: Optional[List[str]] = None  # Add this field
```

### 2. Update the Database Model (Optional)

If you want to store the app usage data directly in the time entry, add a field to your TimeEntry model:

```python
# In your models/time_entry.py or equivalent
from sqlalchemy import Column, String, JSON, Text

class TimeEntry(Base):
    # ... existing fields ...
    app_usage_data = Column(JSON, nullable=True)  # Store as JSON array
    # Or alternatively:
    # app_usage_summary = Column(Text, nullable=True)  # Store as formatted string
```

### 3. Update the Stop Time Tracking Endpoint

Modify your stop time tracking endpoint to handle the app usage data:

```python
@router.post("/stop", response_model=TimeEntryResponse)
def stop_time_tracking(
    employee_id: str,
    time_entry_stop: TimeEntryStop,
    db: Session = Depends(get_db)
):
    """Stop time tracking for an employee"""
    # Find active time entry for employee
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.employee_id == employee_id,
        TimeEntry.is_active == True
    ).first()
    
    if not active_entry:
        raise HTTPException(status_code=404, detail="No active time entry found for employee")
    
    # Update time entry
    active_entry.end_time = datetime.utcnow()
    active_entry.is_active = False
    
    # Calculate duration
    duration = active_entry.end_time - active_entry.start_time
    active_entry.duration_seconds = int(duration.total_seconds())
    
    # Update description and app usage data
    if time_entry_stop.description:
        active_entry.description = time_entry_stop.description
    
    # Handle app usage data - choose one of the approaches below:
    
    # Approach 1: Store in separate field as JSON
    if time_entry_stop.app_usage_data:
        active_entry.app_usage_data = time_entry_stop.app_usage_data
    
    # Approach 2: Append to description
    # if time_entry_stop.app_usage_data:
    #     app_usage_text = "App Usage: " + ", ".join(time_entry_stop.app_usage_data)
    #     if active_entry.description:
    #         active_entry.description += f"\n\n{app_usage_text}"
    #     else:
    #         active_entry.description = app_usage_text
    
    # Approach 3: Store in separate app_usage_summary field
    # if time_entry_stop.app_usage_data:
    #     active_entry.app_usage_summary = ", ".join(time_entry_stop.app_usage_data)
    
    db.commit()
    db.refresh(active_entry)
    
    return active_entry
```

### 4. Update Response Schema (if needed)

If you added app usage fields to the database model, update your response schema:

```python
class TimeEntryResponse(BaseModel):
    # ... existing fields ...
    app_usage_data: Optional[List[str]] = None
    # or
    # app_usage_summary: Optional[str] = None
    
    class Config:
        from_attributes = True
```

### 5. Database Migration (if using Alembic)

If you added database fields, create a migration:

```bash
alembic revision --autogenerate -m "Add app usage data to time entries"
alembic upgrade head
```

## Data Format

The client will send app usage data in this format:
```json
{
  "description": "Optional description",
  "app_usage_data": [
    "Visual Studio Code: 15.2m",
    "Safari: 8.7m",
    "Terminal: 4.1m",
    "Slack: 2.3m"
  ]
}
```

Each item in the `app_usage_data` array follows the format: `"app_name: time"` where time is in minutes with one decimal place.

## Recommended Approach

I recommend **Approach 1** (storing as JSON in a separate field) as it:
- Preserves the structured data
- Allows for easy querying and analysis
- Keeps the description field clean
- Enables future features like app usage analytics

## Testing

You can test the endpoint with curl:

```bash
curl -X POST "http://localhost:8000/api/v1/time-tracking/stop?employee_id=your_employee_id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "description": "Completed feature development",
    "app_usage_data": [
      "Visual Studio Code: 25.5m",
      "Safari: 10.2m",
      "Terminal: 8.1m"
    ]
  }'
``` 