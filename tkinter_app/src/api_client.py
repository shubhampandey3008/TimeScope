import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class APIClient:
    """API client for communicating with the backend system"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = timeout or config.API_TIMEOUT
        self.session = requests.Session()
        self.auth_token = None
        self.employee_id = None
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=config.API_RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     files: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Debug logging
        logger.debug(f"Making {method} request to: {url}")
        logger.debug(f"Headers: {headers}")
        if data and not files:
            # Only log non-sensitive data
            safe_data = data.copy() if data else {}
            if 'password' in safe_data:
                safe_data['password'] = '[REDACTED]'
            logger.debug(f"JSON data: {safe_data}")
        if params:
            logger.debug(f"Query params: {params}")
        
        try:
            if files:
                # Don't set Content-Type for file uploads
                headers.pop("Content-Type", None)
                response = self.session.request(
                    method, url, files=files, data=data, 
                    headers=headers, timeout=self.timeout, params=params
                )
            else:
                response = self.session.request(
                    method, url, json=data, headers=headers, 
                    timeout=self.timeout, params=params
                )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            
            # Log response details for debugging
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                try:
                    response_text = e.response.text
                    logger.error(f"Response body: {response_text}")
                    error_detail = e.response.json()
                    if isinstance(error_detail, dict) and 'detail' in error_detail:
                        raise APIException(f"API Error: {error_detail['detail']}")
                except Exception as parse_error:
                    logger.error(f"Could not parse error response: {parse_error}")
            
            raise APIException(f"API request failed: {e}")
    
    # Employee Management
    def authenticate_employee(self, username: str, password: str) -> Dict:
        """Authenticate employee and get access token"""
        data = {"username": username, "password": password}
        logger.info(f"Sending authentication request to: {self.base_url}/auth/login")
        logger.info(f"Request data: {{'username': '{username}', 'password': '[REDACTED]'}}")
        logger.info(f"Password length: {len(password)}")
        
        response = self._make_request("POST", "/auth/login", data)
        
        if response.get("access_token"):
            self.auth_token = response["access_token"]
            self.employee_id = response.get("employee_id")
            logger.info("Authentication successful - token received")
        else:
            logger.warning(f"Authentication response: {response}")
        
        return response
    
    def create_employee(self, email: str, first_name: str, last_name: str, 
                       phone: str = None, position: str = None) -> Dict:
        """Create a new employee"""
        data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "position": position
        }
        return self._make_request("POST", "/employees/", data)
    
    def get_employees(self, page: int = 1, limit: int = 50) -> Dict:
        """Get list of employees (paginated)"""
        params = {"page": page, "per_page": limit}
        return self._make_request("GET", "/employees/", params=params)
    
    def get_employee(self, employee_id: int = None) -> Dict:
        """Get employee details"""
        emp_id = employee_id or self.employee_id
        return self._make_request("GET", f"/employees/{emp_id}")
    
    def update_employee(self, employee_id: int, data: Dict) -> Dict:
        """Update employee"""
        return self._make_request("PUT", f"/employees/{employee_id}", data)
    
    def deactivate_employee(self, employee_id: int) -> Dict:
        """Deactivate employee"""
        return self._make_request("DELETE", f"/employees/{employee_id}")
    
    def reactivate_employee(self, employee_id: int) -> Dict:
        """Reactivate employee"""
        return self._make_request("POST", f"/employees/{employee_id}/reactivate")

    # Project Management
    def create_project(self, name: str, description: str = None, 
                      project_id: str = None) -> Dict:
        """Create a new project"""
        data = {
            "name": name,
            "description": description,
            "project_id": project_id
        }
        return self._make_request("POST", "/projects/", data)
    
    def get_projects(self, page: int = 1, limit: int = 50) -> Dict:
        """Get list of projects (paginated)"""
        params = {"page": page, "per_page": limit}
        return self._make_request("GET", "/projects/", params=params)
    
    def get_project(self, project_id: int) -> Dict:
        """Get project details"""
        return self._make_request("GET", f"/projects/{project_id}")
    
    def update_project(self, project_id: int, data: Dict) -> Dict:
        """Update project"""
        return self._make_request("PUT", f"/projects/{project_id}", data)
    
    def delete_project(self, project_id: int) -> Dict:
        """Delete project"""
        return self._make_request("DELETE", f"/projects/{project_id}")
    
    def assign_employee_to_project(self, project_id: int, employee_id: str) -> Dict:
        """Assign employee to project"""
        data = {"employee_id": employee_id}
        return self._make_request("POST", f"/projects/{project_id}/employees", data)
    
    def remove_employee_from_project(self, project_id: int, employee_id: int) -> Dict:
        """Remove employee from project"""
        return self._make_request("DELETE", f"/projects/{project_id}/employees/{employee_id}")
    
    def get_project_employees(self, project_id: int) -> Dict:
        """Get employees assigned to project"""
        return self._make_request("GET", f"/projects/{project_id}/employees")

    # Time Tracking
    def create_time_entry(self, employee_id: str, project_id: str, 
                         description: str = None, start_time: str = None) -> Dict:
        """Create time entry"""
        data = {
            "employee_id": employee_id,
            "project_id": project_id,
            "description": description,
            "start_time": start_time or datetime.now().isoformat()
        }
        return self._make_request("POST", "/time-tracking/", data)
    
    def get_time_entries(self, page: int = 1, limit: int = 50, 
                        employee_id: int = None, project_id: int = None) -> Dict:
        """Get time entries (paginated)"""
        params = {"page": page, "per_page": limit}
        if employee_id:
            params["employee_id"] = employee_id
        if project_id:
            params["project_id"] = project_id
        return self._make_request("GET", "/time-tracking/", params=params)
    
    def get_time_entry(self, time_entry_id: int) -> Dict:
        """Get time entry"""
        return self._make_request("GET", f"/time-tracking/{time_entry_id}")
    
    def update_time_entry(self, time_entry_id: int, end_time: str = None, 
                         description: str = None) -> Dict:
        """Update time entry"""
        data = {}
        if end_time:
            data["end_time"] = end_time
        if description:
            data["description"] = description
        return self._make_request("PUT", f"/time-tracking/{time_entry_id}", data)
    
    def delete_time_entry(self, time_entry_id: int) -> Dict:
        """Delete time entry"""
        return self._make_request("DELETE", f"/time-tracking/{time_entry_id}")
    
    def start_time_tracking(self, project_id: str, description: str = None) -> Dict:
        """Start time tracking"""
        data = {
            "project_id": project_id,
            "description": description
        }
        params = {"employee_id": self.employee_id}
        return self._make_request("POST", "/time-tracking/start", data, params=params)
    
    def stop_time_tracking(self, description: str = None, app_usage_data: List[str] = None) -> Dict:
        """Stop time tracking"""
        data = {}
        if description:
            data["description"] = description
        if app_usage_data:
            data["app_usage_data"] = app_usage_data
        params = {"employee_id": self.employee_id}
        return self._make_request("POST", "/time-tracking/stop", data, params=params)
    
    def get_active_time_entry(self, employee_id: int) -> Dict:
        """Get active time entry for employee"""
        return self._make_request("GET", f"/time-tracking/active/{employee_id}")
    
    def get_time_summary(self) -> Dict:
        """Get employee time summaries"""
        return self._make_request("GET", "/time-tracking/summary/employees")

    # Screenshot Management
    def upload_screenshot(self, employee_id: str, time_entry_id: str = None, 
                         permission_granted: bool = False, permission_issue: bool = False,
                         file_path: str = None) -> Dict:
        """Upload screenshot file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'employee_id': employee_id,
                'time_entry_id': time_entry_id,
                'permission_granted': str(permission_granted).lower(),
                'permission_issue': str(permission_issue).lower()
            }
            return self._make_request("POST", "/screenshots/upload", data=data, files=files)
    
    def create_screenshot_record(self, employee_id: str, time_entry_id: str = None,
                               permission_granted: bool = False, permission_issue: bool = False,
                               file_name: str = None, file_path: str = None, 
                               file_size: int = 0, taken_at: str = None) -> Dict:
        """Create screenshot record"""
        data = {
            "employee_id": employee_id,
            "time_entry_id": time_entry_id,
            "permission_granted": permission_granted,
            "permission_issue": permission_issue,
            "file_name": file_name,
            "file_path": file_path,
            "file_size": file_size,
            "taken_at": taken_at or datetime.now().isoformat()
        }
        return self._make_request("POST", "/screenshots/", data)
    
    def get_screenshots(self, page: int = 1, limit: int = 50, 
                       time_entry_id: int = None) -> Dict:
        """Get screenshots (paginated)"""
        params = {"page": page, "per_page": limit}
        if time_entry_id:
            params["time_entry_id"] = time_entry_id
        return self._make_request("GET", "/screenshots/", params=params)
    
    def get_screenshot(self, screenshot_id: int) -> Dict:
        """Get screenshot"""
        return self._make_request("GET", f"/screenshots/{screenshot_id}")
    
    def update_screenshot_permissions(self, screenshot_id: int, 
                                    permission_granted: bool = None, 
                                    permission_issue: bool = None) -> Dict:
        """Update screenshot permissions"""
        data = {}
        if permission_granted is not None:
            data["permission_granted"] = permission_granted
        if permission_issue is not None:
            data["permission_issue"] = permission_issue
        return self._make_request("PUT", f"/screenshots/{screenshot_id}", data)
    
    def delete_screenshot(self, screenshot_id: int) -> Dict:
        """Delete screenshot"""
        return self._make_request("DELETE", f"/screenshots/{screenshot_id}")
    
    def get_permission_summary(self) -> Dict:
        """Get permission summary"""
        return self._make_request("GET", "/screenshots/permissions/summary")
    
    def get_employee_permissions(self, employee_id: int) -> Dict:
        """Get employee permissions"""
        return self._make_request("GET", f"/screenshots/employee/{employee_id}/permissions")

    # Utility Methods
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Health endpoint is not under /api/v1, so we need to use absolute URL
            url = f"{self.base_url.replace('/api/v1', '')}/health"
            headers = {"Content-Type": "application/json"}
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("status") == "healthy"
        except Exception:
            return False
    
    def logout(self):
        """Clear authentication"""
        self.auth_token = None
        self.employee_id = None


class APIException(Exception):
    """Custom exception for API errors"""
    pass 