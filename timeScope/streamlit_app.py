import streamlit as st
import requests
import json
from datetime import datetime, date
from typing import Optional, Dict, Any
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None

def get_auth_headers():
    """Get headers with authentication token"""
    if st.session_state.access_token:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.access_token}"
        }
    return HEADERS

def logout():
    """Logout user and clear session state"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.access_token = None
    st.session_state.is_admin = False
    st.rerun()

def login_user(username: str, password: str):
    """Login user and store credentials"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            headers=HEADERS
        )
        if response.status_code == 200:
            data = response.json()
            # Debug: Print the response data structure
            print(f"Login response data: {data}")
            
            st.session_state.logged_in = True
            st.session_state.user_info = data
            st.session_state.access_token = data["access_token"]
            return True, "Login successful!"
        else:
            error_detail = response.json().get("detail", "Login failed") if response.content else "Login failed"
            return False, error_detail
    except Exception as e:
        return False, f"Error: {str(e)}"

def register_user(employee_data: Dict[str, Any]):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/employees/",
            json=employee_data,
            headers=HEADERS
        )
        if response.status_code == 201:  # Fixed: Employee creation returns 201 Created, not 200
            data = response.json()
            return True, f"Registration successful! Username: {data['username']}, Email: {data['email']}"
        else:
            return False, response.json().get("detail", "Registration failed")
    except Exception as e:
        return False, f"Error: {str(e)}"

# API Helper Functions
def get_employees(page: int = 1, per_page: int = 10, search: str = None):
    """Get list of employees"""
    params = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/employees/",
            params=params,
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching employees: {str(e)}")
        return None

def create_employee(employee_data: Dict[str, Any]):
    """Create a new employee"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/employees/",
            json=employee_data,
            headers=get_auth_headers()
        )
        return response.status_code == 201, response.json()  # Fixed: Employee creation returns 201
    except Exception as e:
        return False, {"detail": str(e)}

def update_employee(employee_id: str, employee_data: Dict[str, Any]):
    """Update an employee"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/employees/{employee_id}",
            json=employee_data,
            headers=get_auth_headers()
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def delete_employee(employee_id: str):
    """Deactivate an employee"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/employees/{employee_id}",
            headers=get_auth_headers()
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_projects(page: int = 1, per_page: int = 10, search: str = None):
    """Get list of projects"""
    params = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/projects/",
            params=params,
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching projects: {str(e)}")
        return None

def create_project(project_data: Dict[str, Any]):
    """Create a new project"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/projects/",
            json=project_data,
            headers=get_auth_headers()
        )
        return response.status_code == 201, response.json()  # Fixed: Project creation returns 201
    except Exception as e:
        return False, {"detail": str(e)}

def update_project(project_id: str, project_data: Dict[str, Any]):
    """Update a project"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/projects/{project_id}",
            json=project_data,
            headers=get_auth_headers()
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def delete_project(project_id: str):
    """Delete a project"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/projects/{project_id}",
            headers=get_auth_headers()
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def assign_employee_to_project(project_id: str, employee_id: str, role: str = "member"):
    """Assign employee to project"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/projects/{project_id}/employees",
            json={"employee_id": employee_id, "role": role},
            headers=get_auth_headers()
        )
        return response.status_code == 201, response.json()  # Fixed: Assignment creation returns 201
    except Exception as e:
        return False, {"detail": str(e)}

def get_time_tracking_data(employee_id: str = None, page: int = 1, per_page: int = 100):
    """Get time tracking data for an employee - simplified to get all data"""
    try:
        params = {
            "page": page,
            "per_page": per_page
        }
        if employee_id:
            params["employee_id"] = employee_id
            
        response = requests.get(
            f"{API_BASE_URL}/time-tracking/",
            params=params,
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def get_active_time_entry(employee_id: str):
    """Get active time entry for an employee"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/time-tracking/active/{employee_id}",
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def start_time_tracking(employee_id: str, project_id: str, description: str = None):
    """Start time tracking for an employee"""
    try:
        data = {"project_id": project_id}
        if description:
            data["description"] = description
            
        response = requests.post(
            f"{API_BASE_URL}/time-tracking/start",
            params={"employee_id": employee_id},
            json=data,
            headers=get_auth_headers()
        )
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def stop_time_tracking(employee_id: str, description: str = None, app_usage_data: list = None):
    """Stop time tracking for an employee"""
    try:
        data = {}
        if description:
            data["description"] = description
        if app_usage_data:
            data["app_usage_data"] = app_usage_data
            
        response = requests.post(
            f"{API_BASE_URL}/time-tracking/stop",
            params={"employee_id": employee_id},
            json=data,
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}

def format_duration(seconds):
    """Format duration from seconds to readable format"""
    if not seconds:
        return "0m"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def format_app_usage_data(app_usage_data):
    """Format app usage data for display"""
    if not app_usage_data:
        return "No app usage data"
    
    formatted_items = []
    for item in app_usage_data:
        if ":" in item:
            app_name, time_str = item.split(":", 1)
            formatted_items.append(f"📱 **{app_name.strip()}**: {time_str.strip()}")
        else:
            formatted_items.append(f"📱 {item}")
    
    return formatted_items

def get_project_name_by_id(project_id: str):
    """Get project name by ID"""
    try:
        projects_data = get_projects(per_page=100)
        if projects_data and projects_data.get('projects'):
            for project in projects_data['projects']:
                if project['id'] == project_id:
                    return project['name']
        return "Unknown Project"
    except:
        return "Unknown Project"

def convert_date_to_datetime_string(date_obj):
    """Convert date object to datetime string for API"""
    if date_obj is None:
        return None
    from datetime import datetime
    # Convert date to datetime at start of day (00:00:00)
    dt = datetime.combine(date_obj, datetime.min.time())
    return dt.isoformat()


# UI Components
def render_login_page():
    """Render login/registration page with separate admin login"""
    st.title("⏰ TimeScope")
    
    tab1, tab2, tab3 = st.tabs(["Employee Login", "Employee Register", "Admin Login"])
    
    with tab1:
        st.header("Employee Login")
        with st.form("employee_login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login as Employee")
            
            if submit:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.header("Register New Employee")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                email = st.text_input("Email *")
            with col2:
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                phone = st.text_input("Phone")
                position = st.text_input("Position")
            
            submit = st.form_submit_button("Register")
            
            if submit:
                if all([first_name, last_name, email, username, password]):
                    employee_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "username": username,
                        "password": password,
                        "phone": phone if phone else None,
                        "position": position if position else None
                    }
                    success, message = register_user(employee_data)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all required fields (marked with *)")
    
    with tab3:
        st.header("Admin Login")
        st.info("🔐 Use static admin credentials to access the admin dashboard")
        
        # Show credentials for testing
        with st.expander("📋 Admin Credentials", expanded=True):
            st.code("Username: admin\nPassword: admin", language="text")
        
        with st.form("admin_login_form"):
            admin_username = st.text_input("Admin Username", placeholder="admin")
            admin_password = st.text_input("Admin Password", type="password", placeholder="admin")
            submit = st.form_submit_button("Login as Admin")
            
            if submit:
                if admin_username and admin_password:
                    # Static admin credentials
                    if admin_username == "admin" and admin_password == "admin":
                        # Set admin session state
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user_info = {
                            "username": "admin",
                            "full_name": "System Administrator",
                            "email": "admin@system.com",
                            "position": "Administrator",
                            "employee_id": "admin-001",
                            "is_admin": True
                        }
                        st.session_state.access_token = "admin-static-token"
                        st.success("✅ Admin login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid admin credentials")
                else:
                    st.error("Please enter both admin username and password")

def render_admin_dashboard():
    """Render admin dashboard with features on main page"""
    st.title("🔧 TimeScope Admin Dashboard")
    
    # Admin navigation in main page with tabs
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["👥 Employees", "📋 Projects", "🔗 Project Assignments"])
    
    with admin_tab1:
        render_employees_section()
    
    with admin_tab2:
        render_projects_section()
    
    with admin_tab3:
        render_project_assignments_section()

def render_employees_section():
    """Render employees management section"""
    st.header("👥 Employee Management")
    
    # Create new employee
    with st.expander("➕ Create New Employee"):
        with st.form("create_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
            with col2:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                phone = st.text_input("Phone")
                position = st.text_input("Position")
            
            submit = st.form_submit_button("Create Employee")
            
            if submit and all([first_name, last_name, email, username, password]):
                employee_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "username": username,
                    "password": password,
                    "phone": phone if phone else None,
                    "position": position if position else None
                }
                success, result = create_employee(employee_data)
                if success:
                    st.success("Employee created successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('detail', 'Unknown error')}")
    
    # Search and list employees
    search_term = st.text_input("🔍 Search Employees", placeholder="Search by name, email, or username")
    
    employees_data = get_employees(search=search_term if search_term else None)
    
    if employees_data:
        st.subheader(f"📋 Employees ({employees_data['total']} total)")
        
        for employee in employees_data["employees"]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"**{employee['full_name']}**")
                    st.write(f"📧 {employee['email']} | 👤 {employee['username']}")
                    if employee.get('position'):
                        st.write(f"💼 {employee['position']}")
                
                with col2:
                    status_color = "🟢" if employee['status'] == 'active' else "🔴"
                    st.write(f"{status_color} Status: {employee['status'].title()}")
                    created_date = employee.get('created_at')
                    if created_date:
                        st.write(f"📅 Created: {created_date[:10]}")
                    else:
                        st.write("📅 Created: N/A")
                
                with col3:
                    if st.button("✏️ Edit", key=f"edit_emp_{employee['id']}"):
                        st.session_state[f"edit_employee_{employee['id']}"] = True
                
                with col4:
                    if employee['status'] == 'active':
                        if st.button("🚫 Deactivate", key=f"deact_emp_{employee['id']}"):
                            success, result = delete_employee(employee['id'])
                            if success:
                                st.success("Employee deactivated!")
                                st.rerun()
                            else:
                                st.error(f"Error: {result.get('detail', 'Unknown error')}")
                
                # Edit form
                if st.session_state.get(f"edit_employee_{employee['id']}", False):
                    with st.form(f"edit_employee_form_{employee['id']}"):
                        st.write("**Edit Employee**")
                        col1, col2 = st.columns(2)
                        with col1:
                            new_first_name = st.text_input("First Name", value=employee['first_name'])
                            new_last_name = st.text_input("Last Name", value=employee['last_name'])
                            new_email = st.text_input("Email", value=employee['email'])
                        with col2:
                            new_username = st.text_input("Username", value=employee['username'])
                            new_phone = st.text_input("Phone", value=employee.get('phone', ''))
                            new_position = st.text_input("Position", value=employee.get('position', ''))
                            new_status = st.selectbox("Status", ['active', 'inactive', 'suspended'], 
                                                    index=['active', 'inactive', 'suspended'].index(employee['status']))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                update_data = {
                                    "first_name": new_first_name,
                                    "last_name": new_last_name,
                                    "email": new_email,
                                    "username": new_username,
                                    "phone": new_phone if new_phone else None,
                                    "position": new_position if new_position else None,
                                    "status": new_status
                                }
                                success, result = update_employee(employee['id'], update_data)
                                if success:
                                    st.success("Employee updated!")
                                    st.session_state[f"edit_employee_{employee['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"Error: {result.get('detail', 'Unknown error')}")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_employee_{employee['id']}"] = False
                                st.rerun()
                
                st.divider()

def render_projects_section():
    """Render projects management section"""
    st.header("📁 Project Management")
    
    # Create new project
    with st.expander("➕ Create New Project"):
        with st.form("create_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Project Name")
                description = st.text_area("Description")
            with col2:
                start_date = st.date_input("Start Date", value=None)
                end_date = st.date_input("End Date", value=None)
            
            submit = st.form_submit_button("Create Project")
            
            if submit and name:
                project_data = {
                    "name": name,
                    "description": description if description else None,
                    "start_date": convert_date_to_datetime_string(start_date),
                    "end_date": convert_date_to_datetime_string(end_date)
                }
                success, result = create_project(project_data)
                if success:
                    st.success("Project created successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('detail', 'Unknown error')}")
    
    # Search and list projects
    search_term = st.text_input("🔍 Search Projects", placeholder="Search by name or description")
    
    projects_data = get_projects(search=search_term if search_term else None)
    
    if projects_data:
        st.subheader(f"📋 Projects ({projects_data['total']} total)")
        
        for project in projects_data["projects"]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"**{project['name']}**")
                    if project.get('description'):
                        st.write(f"📝 {project['description']}")
                
                with col2:
                    status_color = {"active": "🟢", "inactive": "🔴", "completed": "✅", "on_hold": "⏸️"}.get(project['status'], "⚪")
                    st.write(f"{status_color} Status: {project['status'].title()}")
                    if project.get('start_date'):
                        st.write(f"📅 Start: {project['start_date'][:10]}")
                
                with col3:
                    if st.button("✏️ Edit", key=f"edit_proj_{project['id']}"):
                        st.session_state[f"edit_project_{project['id']}"] = True
                
                with col4:
                    if st.button("🗑️ Delete", key=f"del_proj_{project['id']}"):
                        success, result = delete_project(project['id'])
                        if success:
                            st.success("Project deleted!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('detail', 'Unknown error')}")
                
                # Edit form
                if st.session_state.get(f"edit_project_{project['id']}", False):
                    with st.form(f"edit_project_form_{project['id']}"):
                        st.write("**Edit Project**")
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Project Name", value=project['name'])
                            new_description = st.text_area("Description", value=project.get('description', ''))
                        with col2:
                            new_status = st.selectbox("Status", ['active', 'inactive', 'completed', 'on_hold'], 
                                                    index=['active', 'inactive', 'completed', 'on_hold'].index(project['status']))
                            current_start = datetime.fromisoformat(project['start_date'].replace('Z', '+00:00')).date() if project.get('start_date') else None
                            current_end = datetime.fromisoformat(project['end_date'].replace('Z', '+00:00')).date() if project.get('end_date') else None
                            new_start_date = st.date_input("Start Date", value=current_start)
                            new_end_date = st.date_input("End Date", value=current_end)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes"):
                                update_data = {
                                    "name": new_name,
                                    "description": new_description if new_description else None,
                                    "status": new_status,
                                    "start_date": convert_date_to_datetime_string(new_start_date),
                                    "end_date": convert_date_to_datetime_string(new_end_date)
                                }
                                success, result = update_project(project['id'], update_data)
                                if success:
                                    st.success("Project updated!")
                                    st.session_state[f"edit_project_{project['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"Error: {result.get('detail', 'Unknown error')}")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_project_{project['id']}"] = False
                                st.rerun()
                
                st.divider()


def render_project_assignments_section():
    """Render project assignments section"""
    st.header("👥 Project Assignments")
    
    # Get data for assignments
    projects_data = get_projects(per_page=100)
    employees_data = get_employees(per_page=100)
    
    if not projects_data or not employees_data:
        st.warning("Make sure you have both projects and employees before making assignments.")
        return
    
    project_options = {proj['name']: proj['id'] for proj in projects_data['projects']}
    employee_options = {f"{emp['full_name']} ({emp['username']})": emp['id'] for emp in employees_data['employees']}
    
    # Assign employee to project
    with st.expander("➕ Assign Employee to Project"):
        with st.form("assign_employee_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_project = st.selectbox("Select Project", options=list(project_options.keys()))
            with col2:
                selected_employee = st.selectbox("Select Employee", options=list(employee_options.keys()))
            with col3:
                role = st.selectbox("Role", options=["member", "lead", "manager"])
            
            submit = st.form_submit_button("Assign Employee")
            
            if submit:
                success, result = assign_employee_to_project(
                    project_options[selected_project],
                    employee_options[selected_employee],
                    role
                )
                if success:
                    st.success("Employee assigned successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('detail', 'Unknown error')}")
    
    st.info("💡 **Note**: You can view project assignments by going to the Projects section and checking individual project details.")

def render_user_dashboard():
    """Render enhanced user dashboard with time tracking"""
    st.title("👤 TimeScope User Dashboard")
    user_name = st.session_state.user_info.get('full_name', 'Unknown User')
    employee_id = st.session_state.user_info.get('employee_id')
    st.write(f"Welcome, **{user_name}**!")
    
    # User info
    with st.expander("📊 Your Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Full Name:** {st.session_state.user_info.get('full_name', 'N/A')}")
            st.write(f"**Username:** {st.session_state.user_info.get('username', 'N/A')}")
            st.write(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
        with col2:
            position = st.session_state.user_info.get('position')
            if position:
                st.write(f"**Position:** {position}")
            else:
                st.write("**Position:** Not specified")
            st.write(f"**Employee ID:** {employee_id}")
    
    if not employee_id:
        st.error("❌ Employee ID not found. Please log in again.")
        return
    
    # Time Tracking Section
    st.header("⏱️ Time Tracking")
    
    # Check for active session
    success, active_entry = get_active_time_entry(employee_id)
    if success and active_entry:
        st.success("🟢 **Active Time Tracking Session**")
        with st.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"📝 **Description:** {active_entry.get('description', 'No description')}")
                st.write(f"🚀 **Started:** {active_entry['start_time'][:19].replace('T', ' ')}")
                st.write(f"📋 **Project ID:** {active_entry['project_id']}")
            with col2:
                if st.button("⏹️ Stop Tracking", type="primary"):
                    stop_success, stop_result = stop_time_tracking(employee_id)
                    if stop_success:
                        st.success("✅ Time tracking stopped!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error stopping: {stop_result.get('detail', 'Unknown error')}")
    else:
        st.info("⏸️ No active time tracking session")
    
    # Get ALL time tracking data (no filters)
    st.subheader("📋 All Time Tracking Sessions")
    success, tracking_data = get_time_tracking_data(employee_id=employee_id, per_page=100)
    
    if success and tracking_data and tracking_data.get('time_entries'):
        st.write(f"**Total Sessions Found:** {tracking_data['total']}")
        st.divider()
        
        # Display each session with app usage data
        for i, entry in enumerate(tracking_data['time_entries']):
            st.subheader(f"🕒 Session {i+1}")
            
            # Session basic info
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**📅 Date:** {entry['start_time'][:10]}")
                st.write(f"**🕐 Time:** {entry['start_time'][11:19]} - {entry.get('end_time', 'Active')[11:19] if entry.get('end_time') else 'Still Active'}")
                st.write(f"**⏱️ Duration:** {format_duration(entry.get('duration_seconds', 0))}")
                st.write(f"**📋 Project ID:** {entry['project_id']}")
                if entry.get('description'):
                    st.write(f"**📝 Description:** {entry['description']}")
                status = "🟢 Active" if entry.get('is_active') else "⚪ Completed"
                st.write(f"**Status:** {status}")
            
            with col2:
                st.write("**Entry Details:**")
                st.write(f"ID: {entry.get('id', 'N/A')}")
                st.write(f"Employee: {entry.get('employee_id', 'N/A')}")
            
            # App Usage Data - Primary Focus
            st.write("### 📱 App Usage Data:")
            if entry.get('app_usage_data'):
                st.success("✅ App usage data available!")
                for app_item in entry['app_usage_data']:
                    if ":" in app_item:
                        app_name, time_str = app_item.split(":", 1)
                        st.markdown(f"**📱 {app_name.strip()}:** `{time_str.strip()}`")
                    else:
                        st.markdown(f"**📱** `{app_item}`")
            else:
                st.warning("⚠️ No app usage data recorded for this session")
            
            # Debug info (can be removed later)
            with st.expander("🔍 Raw Data (Debug)", expanded=False):
                st.json(entry)
            
            st.divider()
    
    elif success and tracking_data:
        st.info("📭 No time tracking sessions found.")
        st.write("**Debug Info:**")
        st.write(f"API Response: {tracking_data}")
    else:
        st.error(f"❌ Error loading time tracking data")
        st.write(f"**Error Details:** {tracking_data if tracking_data else 'No response from API'}")

# Main App
def main():
    st.set_page_config(
        page_title="TimeScope",
        page_icon="⏰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stButton > button {
            width: 100%;
        }
        .status-active { color: green; }
        .status-inactive { color: red; }
        
        /* Time tracking specific styles */
        .time-entry {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .app-usage-item {
            background-color: #e3f2fd;
            padding: 0.5rem;
            border-radius: 0.25rem;
            margin: 0.25rem 0;
            border-left: 3px solid #2196f3;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        render_login_page()
    else:
        # Header with logout
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown('<h1 class="main-header">⏰ TimeScope</h1>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 Logout"):
                logout()
        
        # Check if user is admin
        is_admin = st.session_state.user_info.get('is_admin', False)
        
        # User info in sidebar
        with st.sidebar:
            st.write(f"👤 **{st.session_state.user_info.get('full_name', 'Unknown User')}**")
            st.write(f"📧 {st.session_state.user_info.get('email', 'No email')}")
            if st.session_state.user_info.get('position'):
                st.write(f"💼 {st.session_state.user_info['position']}")
            st.divider()
            
            if is_admin:
                # Admin user - show admin mode indicator
                st.success("🔧 **Admin Mode**")
                st.write("You are logged in as an administrator")
                view_mode = "admin"  # Force admin mode
            else:
                # Regular employee - show view mode toggle
                st.subheader("🎛️ View Mode")
                view_mode = st.radio(
                    "Choose view:",
                    ["👤 User Dashboard", "🔧 Admin Dashboard"],
                    index=0
                )
        
        # Render dashboards in main content area (outside sidebar)
        if is_admin or view_mode == "🔧 Admin Dashboard":
            render_admin_dashboard()
        else:
            render_user_dashboard()

if __name__ == "__main__":
    main() 