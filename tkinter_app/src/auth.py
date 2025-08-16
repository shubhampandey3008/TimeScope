import keyring
import logging
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64
import os

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class AuthManager:
    """Handles authentication and secure credential storage"""
    
    def __init__(self):
        self.service_name = "SystemMonitoringApp"
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.current_user = None
        self.session_start = None
        self.session_timeout = config.SESSION_TIMEOUT
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_name = f"{self.service_name}_encryption_key"
        
        try:
            # Try to get existing key
            key_str = keyring.get_password(self.service_name, key_name)
            if key_str:
                return key_str.encode()
        except Exception as e:
            logger.warning(f"Could not retrieve encryption key: {e}")
        
        # Create new key
        key = Fernet.generate_key()
        try:
            keyring.set_password(self.service_name, key_name, key.decode())
        except Exception as e:
            logger.warning(f"Could not store encryption key: {e}")
        
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not config.ENCRYPT_DATA:
            return data
        
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not config.ENCRYPT_DATA:
            return encrypted_data
        
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def store_credentials(self, username: str, password: str, 
                         employee_data: Dict = None) -> bool:
        """Store user credentials securely"""
        if not config.STORE_CREDENTIALS:
            return False
        
        try:
            # Store encrypted password
            encrypted_password = self.encrypt_data(password)
            keyring.set_password(self.service_name, username, encrypted_password)
            
            # Store additional employee data
            if employee_data:
                data_key = f"{username}_employee_data"
                encrypted_data = self.encrypt_data(json.dumps(employee_data))
                keyring.set_password(self.service_name, data_key, encrypted_data)
            
            logger.info(f"Credentials stored for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def get_stored_credentials(self, username: str) -> Optional[Dict]:
        """Retrieve stored credentials"""
        if not config.STORE_CREDENTIALS:
            return None
        
        try:
            # Get password
            encrypted_password = keyring.get_password(self.service_name, username)
            if not encrypted_password:
                return None
            
            password = self.decrypt_data(encrypted_password)
            
            # Get employee data
            data_key = f"{username}_employee_data"
            encrypted_data = keyring.get_password(self.service_name, data_key)
            employee_data = {}
            
            if encrypted_data:
                decrypted_data = self.decrypt_data(encrypted_data)
                employee_data = json.loads(decrypted_data)
            
            return {
                "username": username,
                "password": password,
                "employee_data": employee_data
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {e}")
            return None
    
    def get_stored_usernames(self) -> List[str]:
        """Get list of stored usernames"""
        # This is a limitation of keyring - we can't easily enumerate stored credentials
        # We'll store a list of usernames separately
        try:
            usernames_data = keyring.get_password(self.service_name, "stored_usernames")
            if usernames_data:
                decrypted = self.decrypt_data(usernames_data)
                return json.loads(decrypted)
            return []
        except Exception as e:
            logger.error(f"Failed to get stored usernames: {e}")
            return []
    
    def add_stored_username(self, username: str):
        """Add username to stored list"""
        try:
            usernames = self.get_stored_usernames()
            if username not in usernames:
                usernames.append(username)
                encrypted_data = self.encrypt_data(json.dumps(usernames))
                keyring.set_password(self.service_name, "stored_usernames", encrypted_data)
        except Exception as e:
            logger.error(f"Failed to add username: {e}")
    
    def remove_stored_credentials(self, username: str) -> bool:
        """Remove stored credentials"""
        try:
            keyring.delete_password(self.service_name, username)
            
            # Remove employee data
            data_key = f"{username}_employee_data"
            try:
                keyring.delete_password(self.service_name, data_key)
            except:
                pass
            
            # Remove from username list
            usernames = self.get_stored_usernames()
            if username in usernames:
                usernames.remove(username)
                encrypted_data = self.encrypt_data(json.dumps(usernames))
                keyring.set_password(self.service_name, "stored_usernames", encrypted_data)
            
            logger.info(f"Credentials removed for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove credentials: {e}")
            return False
    
    def login(self, username: str, password: str, employee_data: Dict = None) -> bool:
        """Login user and start session"""
        try:
            self.current_user = {
                "username": username,
                "employee_data": employee_data or {}
            }
            self.session_start = datetime.now()
            
            # Store credentials if requested
            if config.STORE_CREDENTIALS:
                self.store_credentials(username, password, employee_data)
                self.add_stored_username(username)
            
            logger.info(f"User logged in: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def logout(self):
        """Logout user and clear session"""
        if self.current_user:
            username = self.current_user.get("username")
            logger.info(f"User logged out: {username}")
        
        self.current_user = None
        self.session_start = None
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_user is not None
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        if not self.is_logged_in() or not self.session_start:
            return False
        
        if self.session_timeout <= 0:
            return True  # No timeout
        
        elapsed = datetime.now() - self.session_start
        return elapsed.total_seconds() < self.session_timeout
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information"""
        if not self.is_session_valid():
            return None
        return self.current_user
    
    def get_session_info(self) -> Dict:
        """Get session information"""
        if not self.is_logged_in():
            return {"logged_in": False}
        
        elapsed = 0
        remaining = 0
        
        if self.session_start:
            elapsed = (datetime.now() - self.session_start).total_seconds()
            if self.session_timeout > 0:
                remaining = max(0, self.session_timeout - elapsed)
        
        return {
            "logged_in": True,
            "username": self.current_user.get("username"),
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "session_valid": self.is_session_valid()
        }
    
    def extend_session(self):
        """Extend current session"""
        if self.is_logged_in():
            self.session_start = datetime.now()
    
    def clear_all_stored_data(self) -> bool:
        """Clear all stored authentication data"""
        try:
            usernames = self.get_stored_usernames()
            for username in usernames:
                self.remove_stored_credentials(username)
            
            # Clear username list
            keyring.delete_password(self.service_name, "stored_usernames")
            
            # Clear encryption key
            key_name = f"{self.service_name}_encryption_key"
            keyring.delete_password(self.service_name, key_name)
            
            logger.info("All stored authentication data cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear stored data: {e}")
            return False 