import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.root = tk.Tk()
        self.current_page = None
        self.timer_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.selected_project = None
        self.projects = []
        
        self.setup_window()
        self.setup_styles()
        self.show_login_page()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("TimeScope")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(config.WINDOW_RESIZABLE, config.WINDOW_RESIZABLE)
        
        if config.ALWAYS_ON_TOP:
            self.root.attributes('-topmost', True)
        
        # Center window on screen
        self.center_window()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Setup UI styles"""
        style = ttk.Style()
        
        # Configure styles based on theme
        if config.THEME == "dark":
            style.theme_use('clam')
            
            # Configure TTK styles with better dark theme support
            style.configure('TLabel', 
                          background='#2d2d2d', 
                          foreground='white',
                          borderwidth=0)
            
            style.configure('TButton', 
                          background='#4CAF50', 
                          foreground='white',
                          borderwidth=1,
                          focuscolor='none',
                          lightcolor='#5CBF60',
                          darkcolor='#3E8E41')
            
            style.configure('TFrame', 
                          background='#2d2d2d',
                          borderwidth=0)
            
            style.configure('TEntry', 
                          background='#404040', 
                          foreground='white', 
                          fieldbackground='#404040',
                          borderwidth=1,
                          insertcolor='white')
            
            style.configure('TCheckbutton', 
                          background='#2d2d2d', 
                          foreground='white',
                          focuscolor='none',
                          indicatorcolor='#404040')
            
            # Enhanced Combobox styling for better readability
            style.configure('TCombobox', 
                          background='#404040', 
                          foreground='white', 
                          fieldbackground='#404040',
                          borderwidth=1,
                          arrowcolor='white',
                          insertcolor='white',
                          selectbackground='#4CAF50',
                          selectforeground='white')
            
            # Style the combobox popdown listbox
            style.configure('TCombobox.Listbox',
                          background='#404040',
                          foreground='white',
                          selectbackground='#4CAF50',
                          selectforeground='white',
                          borderwidth=1)
            
            style.configure('TLabelFrame', 
                          background='#2d2d2d', 
                          foreground='white',
                          borderwidth=1,
                          relief='groove')
            
            style.configure('TLabelFrame.Label', 
                          background='#2d2d2d', 
                          foreground='white')
            
            style.configure('TScrollbar', 
                          background='#404040', 
                          troughcolor='#2d2d2d', 
                          bordercolor='#555555',
                          arrowcolor='white',
                          darkcolor='#555555',
                          lightcolor='#666666')
            
            # Map styles for better interaction feedback
            style.map('TButton', 
                     background=[('active', '#5CBF60'), ('pressed', '#3E8E41'), ('disabled', '#555555')],
                     foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#999999')])
            
            style.map('TEntry',
                     focuscolor=[('focus', '#4CAF50')],
                     bordercolor=[('focus', '#4CAF50')])
            
            style.map('TCombobox',
                     focuscolor=[('focus', '#4CAF50')],
                     bordercolor=[('focus', '#4CAF50')],
                     selectbackground=[('focus', '#4CAF50')],
                     selectforeground=[('focus', 'white')])
            
            style.map('TScrollbar',
                     background=[('active', '#555555'), ('pressed', '#666666')])
            
            style.map('TCheckbutton',
                     background=[('active', '#2d2d2d')],
                     foreground=[('active', 'white')])
            
            # Set root window background for dark theme
            self.root.configure(bg='#2d2d2d')
            
            # Configure additional widget options for dark theme
            self.root.option_add('*TCombobox*Listbox.background', '#404040')
            self.root.option_add('*TCombobox*Listbox.foreground', 'white')
            self.root.option_add('*TCombobox*Listbox.selectBackground', '#4CAF50')
            self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
            
            # Define theme colors
            self.bg_color = '#2d2d2d'
            self.fg_color = 'white'
            self.entry_bg_color = '#404040'
            self.entry_fg_color = 'white'
            self.button_bg_color = '#4CAF50'
            self.button_fg_color = 'white'
            self.border_color = '#555555'
            self.status_color = '#cccccc'
            self.error_color = '#ff6b6b'
            self.success_color = '#51cf66'
            self.info_color = '#74c0fc'
        else:
            style.theme_use('default')
            
            # Light theme configurations
            style.configure('TLabel', 
                          background='#f0f0f0', 
                          foreground='#333333')
            
            style.configure('TButton', 
                          background='#4CAF50', 
                          foreground='white')
            
            style.configure('TFrame', 
                          background='#f0f0f0')
            
            style.configure('TEntry', 
                          background='white', 
                          foreground='black', 
                          fieldbackground='white')
            
            style.configure('TCheckbutton', 
                          background='#f0f0f0', 
                          foreground='#333333')
            
            style.configure('TCombobox', 
                          background='white', 
                          foreground='black', 
                          fieldbackground='white')
            
            style.configure('TLabelFrame', 
                          background='#f0f0f0', 
                          foreground='#333333')
            
            style.configure('TLabelFrame.Label', 
                          background='#f0f0f0', 
                          foreground='#333333')
            
            # Set root window background for light theme
            self.root.configure(bg='#f0f0f0')
            
            # Define theme colors
            self.bg_color = '#f0f0f0'
            self.fg_color = '#333333'
            self.entry_bg_color = 'white'
            self.entry_fg_color = 'black'
            self.button_bg_color = '#4CAF50'
            self.button_fg_color = 'white'
            self.border_color = '#cccccc'
            self.status_color = '#666666'
            self.error_color = '#d32f2f'
            self.success_color = '#388e3c'
            self.info_color = '#1976d2'
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_page(self):
        """Show login page"""
        self.clear_window()
        self.current_page = "login"
        
        # Main container with theme-aware background
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="TimeScope", 
                              font=("Arial", 18, "bold"), bg=self.bg_color, fg=self.fg_color)
        title_label.pack(pady=(20, 30))
        
        # Form frame using grid for clean layout
        form_frame = tk.Frame(main_frame, bg=self.bg_color)
        form_frame.pack(pady=20)
        
        # Configure grid columns
        form_frame.columnconfigure(1, weight=1)
        
        # Username with Text widget for better visibility
        tk.Label(form_frame, text="Username:", bg=self.bg_color, fg=self.fg_color, 
                font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='e', padx=(0, 10), pady=10)
        
        username_frame = tk.Frame(form_frame, bg=self.border_color, relief="solid", bd=2)
        username_frame.grid(row=0, column=1, sticky='w', pady=10)
        self.username_entry = tk.Text(username_frame, width=25, height=1, bg=self.entry_bg_color, fg=self.entry_fg_color, 
                                     font=("Arial", 12), relief="flat", bd=0, wrap='none', insertbackground=self.entry_fg_color)
        self.username_entry.pack(padx=2, pady=2)
        
        # Add focus events for better visual feedback
        def on_username_focus_in(event):
            username_frame.config(bg='#4CAF50' if config.THEME == "dark" else '#2196F3', bd=3)
        def on_username_focus_out(event):
            username_frame.config(bg=self.border_color, bd=2)
        self.username_entry.bind('<FocusIn>', on_username_focus_in)
        self.username_entry.bind('<FocusOut>', on_username_focus_out)
        
        # Password - using Entry widget with theme colors
        tk.Label(form_frame, text="Password:", bg=self.bg_color, fg=self.fg_color, 
                font=("Arial", 12, "bold")).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=10)
        
        password_frame = tk.Frame(form_frame, bg=self.border_color, relief="solid", bd=2)
        password_frame.grid(row=1, column=1, sticky='w', pady=10)
        self.password_entry = tk.Entry(password_frame, width=25, show='*', font=("Arial", 12),
                                      bg=self.entry_bg_color, fg=self.entry_fg_color, relief="flat", bd=0,
                                      insertbackground=self.entry_fg_color)
        self.password_entry.pack(padx=2, pady=2)
        
        # Add focus events for better visual feedback
        def on_password_focus_in(event):
            password_frame.config(bg='#4CAF50' if config.THEME == "dark" else '#2196F3', bd=3)
        def on_password_focus_out(event):
            password_frame.config(bg=self.border_color, bd=2)
        self.password_entry.bind('<FocusIn>', on_password_focus_in)
        self.password_entry.bind('<FocusOut>', on_password_focus_out)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar(value=config.STORE_CREDENTIALS)
        remember_check = tk.Checkbutton(form_frame, text="Remember credentials", 
                                       variable=self.remember_var, bg=self.bg_color, fg=self.fg_color, 
                                       font=("Arial", 10), selectcolor=self.entry_bg_color,
                                       activebackground=self.bg_color, activeforeground=self.fg_color)
        remember_check.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Login button
        login_button = ttk.Button(form_frame, text="LOGIN", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Please enter your credentials", 
                                    foreground=self.status_color, bg=self.bg_color, font=("Arial", 10))
        self.status_label.pack(pady=10)
        
        # Stored credentials dropdown
        self.setup_stored_credentials(main_frame)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
        # Set focus and update
        self.root.update_idletasks()
        self.username_entry.focus_set()
        
        logger.info(f"Login page created with {config.THEME} theme")
    
    def setup_stored_credentials(self, parent):
        """Setup stored credentials dropdown"""
        try:
            stored_usernames = self.app_controller.auth_manager.get_stored_usernames()
            if stored_usernames:
                # Create a frame for stored credentials with theme colors
                stored_frame = tk.Frame(parent, bg=self.bg_color)
                stored_frame.pack(pady=(20, 10))
                
                stored_label = tk.Label(stored_frame, text="Stored Accounts:", 
                                      bg=self.bg_color, fg=self.fg_color, font=("Arial", 10))
                stored_label.pack(anchor=tk.W)
                
                combo_frame = tk.Frame(stored_frame, bg=self.bg_color)
                combo_frame.pack(fill=tk.X, pady=(5, 0))
                
                self.stored_combo = ttk.Combobox(combo_frame, values=stored_usernames, width=27, state="readonly")
                self.stored_combo.pack(side=tk.LEFT, padx=(0, 10))
                self.stored_combo.bind('<<ComboboxSelected>>', self.load_stored_credentials)
                
                load_button = ttk.Button(combo_frame, text="Load", command=self.load_stored_credentials)
                load_button.pack(side=tk.LEFT)
        except Exception as e:
            logger.error(f"Error setting up stored credentials: {e}")
    
    def load_stored_credentials(self, event=None):
        """Load stored credentials"""
        try:
            if hasattr(self, 'stored_combo'):
                username = self.stored_combo.get()
                if username:
                    credentials = self.app_controller.auth_manager.get_stored_credentials(username)
                    if credentials:
                        self.username_entry.delete("1.0", tk.END)
                        self.username_entry.insert("1.0", credentials['username'])
                        self.password_entry.delete(0, tk.END)
                        self.password_entry.insert(0, credentials['password'])
        except Exception as e:
            logger.error(f"Error loading stored credentials: {e}")
    
    def login(self):
        """Handle login"""
        logger.info("Login button clicked!")
        
        username = self.username_entry.get("1.0", "end-1c").strip()
        password = self.password_entry.get().strip()
        
        logger.info(f"Username: '{username}', Password length: {len(password)}")
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password", fg=self.error_color)
            logger.warning("Username or password is empty")
            return
        
        self.status_label.config(text="Logging in...", fg=self.info_color)
        self.root.update()
        
        logger.info("Starting login thread...")
        # Login in background thread
        thread = threading.Thread(target=self._login_thread, args=(username, password))
        thread.daemon = True
        thread.start()
    
    def _login_thread(self, username, password):
        """Login in background thread"""
        try:
            logger.info(f"Login thread started for user: {username}")
            success = self.app_controller.login(username, password)
            logger.info(f"Login result: {success}")
            
            # Update UI in main thread
            if success:
                self.root.after(0, self._handle_login_result, True)
            else:
                # Get the last error from logs or use a generic message
                error_msg = "Login failed. Please check your credentials and ensure your password is at least 6 characters."
                self.root.after(0, self._handle_login_result, False, error_msg)
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, self._handle_login_result, False, str(e))
    
    def _handle_login_result(self, success, error_msg=None):
        """Handle login result"""
        logger.info(f"Login result handler called: success={success}, error={error_msg}")
        
        if success:
            self.status_label.config(text="Login successful!", fg=self.success_color)
            logger.info("Login successful, showing main page in 1 second")
            self.root.after(1000, self.show_main_page)
        else:
            error_text = error_msg or "Login failed. Please check your credentials."
            self.status_label.config(text=error_text, fg=self.error_color)
            logger.error(f"Login failed: {error_text}")
    
    def show_main_page(self):
        """Show main application page"""
        self.clear_window()
        self.current_page = "main"
        
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame - user info and logout
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        user_info = self.app_controller.auth_manager.get_current_user()
        username = user_info.get('username', 'Unknown') if user_info else 'Unknown'
        
        ttk.Label(top_frame, text=f"Welcome, {username}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        logout_button = ttk.Button(top_frame, text="Logout", command=self.logout)
        logout_button.pack(side=tk.RIGHT)
        
        # Project selection frame
        project_frame = ttk.LabelFrame(main_container, text="Project Selection", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Project dropdown
        ttk.Label(project_frame, text="Project:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.project_combo = ttk.Combobox(project_frame, width=40, state="readonly")
        self.project_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        self.project_combo.bind('<<ComboboxSelected>>', self.on_project_selected)
        
        # Refresh button
        refresh_button = ttk.Button(project_frame, text="Refresh", command=self.refresh_projects)
        refresh_button.grid(row=0, column=2, pady=5, padx=(10, 0))
        
        project_frame.columnconfigure(1, weight=1)
        
        # Time tracking frame
        timer_frame = ttk.LabelFrame(main_container, text="Time Tracking", padding="10")
        timer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Timer display
        self.timer_label = ttk.Label(timer_frame, text="00:00:00", font=("Arial", 20, "bold"))
        self.timer_label.pack(pady=10)
        
        # Start/Stop button
        self.start_stop_button = ttk.Button(timer_frame, text="Start Tracking", 
                                           command=self.toggle_tracking)
        self.start_stop_button.pack(pady=5)
        
        # Status label
        self.tracking_status_label = ttk.Label(timer_frame, text="Ready to start tracking")
        self.tracking_status_label.pack(pady=5)
        
        # Activity monitoring frame
        activity_frame = ttk.LabelFrame(main_container, text="Current Activity", padding="10")
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Activity info with theme-aware colors
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=8, width=80,
                                                      bg=self.entry_bg_color, fg=self.entry_fg_color,
                                                      insertbackground=self.entry_fg_color)
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame - controls
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill=tk.X)
        
        # Manual screenshot button
        screenshot_button = ttk.Button(bottom_frame, text="Take Screenshot", 
                                     command=self.take_manual_screenshot)
        screenshot_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings button
        settings_button = ttk.Button(bottom_frame, text="Settings", command=self.show_settings)
        settings_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status bar
        self.status_bar = ttk.Label(bottom_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Load projects
        self.refresh_projects()
        
        # Start UI update timer
        self.update_timer()
    
    def refresh_projects(self):
        """Refresh projects"""
        self.status_bar.config(text="Loading projects...")
        thread = threading.Thread(target=self._refresh_projects_thread)
        thread.daemon = True
        thread.start()
    
    def _refresh_projects_thread(self):
        """Refresh projects in background thread"""
        try:
            projects = self.app_controller.get_projects()
            self.root.after(0, self._update_projects, projects)
        except Exception as e:
            logger.error(f"Error refreshing projects: {e}")
            self.root.after(0, self._update_projects, [])
    
    def _update_projects(self, projects):
        """Update projects dropdown"""
        self.projects = projects
        project_names = [f"{p['name']} (ID: {p['id']})" for p in projects]
        self.project_combo['values'] = project_names
        
        if projects:
            self.project_combo.current(0)
            self.on_project_selected()
        
        self.status_bar.config(text=f"Loaded {len(projects)} projects")
    
    def on_project_selected(self, event=None):
        """Handle project selection"""
        if not self.projects:
            return
        
        try:
            selected_index = self.project_combo.current()
            if selected_index >= 0:
                self.selected_project = self.projects[selected_index]
        except Exception as e:
            logger.error(f"Error selecting project: {e}")
    
    def toggle_tracking(self):
        """Toggle time tracking"""
        if self.timer_running:
            self.stop_tracking()
        else:
            self.start_tracking()
    
    def start_tracking(self):
        """Start time tracking"""
        if not self.selected_project:
            messagebox.showerror("Error", "Please select a project first")
            return
        
        try:
            # Start tracking via controller
            success = self.app_controller.start_tracking(self.selected_project['id'])
            
            if success:
                self.timer_running = True
                self.start_time = datetime.now()
                self.elapsed_time = 0
                
                self.start_stop_button.config(text="Stop Tracking")
                self.tracking_status_label.config(text=f"Tracking: {self.selected_project['name']}")
                
                # Update activity display
                self.update_activity_display()
                
                self.status_bar.config(text="Time tracking started")
            else:
                messagebox.showerror("Error", "Failed to start time tracking")
                
        except Exception as e:
            logger.error(f"Error starting tracking: {e}")
            messagebox.showerror("Error", f"Failed to start tracking: {e}")
    
    def stop_tracking(self):
        """Stop time tracking"""
        try:
            success = self.app_controller.stop_tracking()
            
            if success:
                self.timer_running = False
                self.start_stop_button.config(text="Start Tracking")
                self.tracking_status_label.config(text="Tracking stopped")
                self.status_bar.config(text="Time tracking stopped")
            else:
                messagebox.showerror("Error", "Failed to stop time tracking")
                
        except Exception as e:
            logger.error(f"Error stopping tracking: {e}")
            messagebox.showerror("Error", f"Failed to stop tracking: {e}")
    
    def update_timer(self):
        """Update timer display"""
        if self.timer_running and self.start_time:
            self.elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        # Only update timer label if it exists (i.e., we're on the main page)
        if hasattr(self, 'timer_label'):
            # Format time
            hours = int(self.elapsed_time // 3600)
            minutes = int((self.elapsed_time % 3600) // 60)
            seconds = int(self.elapsed_time % 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            
            # Update activity display periodically
            if self.timer_running and int(self.elapsed_time) % 30 == 0:  # Every 30 seconds
                self.update_activity_display()
        
        # Schedule next update
        self.root.after(1000, self.update_timer)
    
    def update_activity_display(self):
        """Update activity display"""
        try:
            # Only update if activity text widget exists
            if not hasattr(self, 'activity_text'):
                return
                
            activity_data = self.app_controller.get_current_activity()
            
            # Clear and update text
            self.activity_text.delete(1.0, tk.END)
            
            lines = []
            lines.append(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Session Duration: {self.format_duration(self.elapsed_time)}")
            lines.append("")
            
            if activity_data:
                lines.append(f"Current App: {activity_data.get('current_app', 'None')}")
                lines.append(f"Current Website: {activity_data.get('current_website', 'None')}")
                lines.append(f"System Idle: {'Yes' if activity_data.get('is_idle') else 'No'}")
                lines.append("")
                
                # App usage summary
                app_usage = self.app_controller.get_app_usage_summary()
                if app_usage:
                    lines.append("Top Applications:")
                    sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
                    for app, duration in sorted_apps:
                        lines.append(f"  {app}: {self.format_duration(duration)}")
                    lines.append("")
                
                # Website usage summary
                website_usage = self.app_controller.get_website_usage_summary()
                if website_usage:
                    lines.append("Top Websites:")
                    sorted_sites = sorted(website_usage.items(), key=lambda x: x[1], reverse=True)[:5]
                    for site, duration in sorted_sites:
                        lines.append(f"  {site}: {self.format_duration(duration)}")
            
            self.activity_text.insert(tk.END, "\n".join(lines))
            
        except Exception as e:
            logger.error(f"Error updating activity display: {e}")
    
    def format_duration(self, seconds):
        """Format duration in seconds to readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def take_manual_screenshot(self):
        """Take manual screenshot"""
        try:
            success = self.app_controller.take_manual_screenshot()
            if success:
                self.status_bar.config(text="Screenshot captured")
            else:
                self.status_bar.config(text="Screenshot failed")
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            self.status_bar.config(text="Screenshot error")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet")
    
    def logout(self):
        """Logout user"""
        if self.timer_running:
            if messagebox.askyesno("Confirm", "Time tracking is active. Stop tracking and logout?"):
                self.stop_tracking()
            else:
                return
        
        self.app_controller.logout()
        self.show_login_page()
    
    def on_closing(self):
        """Handle window closing"""
        if self.timer_running:
            if messagebox.askyesno("Confirm", "Time tracking is active. Stop tracking and exit?"):
                self.stop_tracking()
            else:
                return
        
        self.app_controller.shutdown()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop() 