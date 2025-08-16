import os
import time
import threading
import logging
from datetime import datetime
from typing import Optional, Dict, List
import tempfile
import uuid

try:
    import pyautogui
    from PIL import Image, ImageDraw, ImageFont
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

try:
    import config
except ImportError:
    import config.example as config

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Manages screenshot capture and processing"""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.capturing = False
        self.capture_thread = None
        self.screenshots_dir = "screenshots"
        self.screenshot_queue = []
        self.last_capture_time = None
        
        # Check screenshot capabilities
        if not SCREENSHOT_AVAILABLE:
            logger.warning("Screenshot libraries not available - screenshot capture disabled")
        
        # Create screenshots directory
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Disable pyautogui failsafe
        if SCREENSHOT_AVAILABLE:
            pyautogui.FAILSAFE = False
    
    def start_capture(self, time_entry_id: int):
        """Start automatic screenshot capture"""
        if not config.SCREENSHOT_ENABLED or not SCREENSHOT_AVAILABLE:
            logger.info("Screenshot capture disabled")
            return
        
        if self.capturing:
            return
        
        self.capturing = True
        self.time_entry_id = time_entry_id
        self.capture_thread = threading.Thread(
            target=self._capture_loop, 
            daemon=True
        )
        self.capture_thread.start()
        logger.info(f"Screenshot capture started for time entry {time_entry_id}")
    
    def stop_capture(self):
        """Stop automatic screenshot capture"""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        logger.info("Screenshot capture stopped")
    
    def _capture_loop(self):
        """Main screenshot capture loop"""
        while self.capturing:
            try:
                if self._should_capture():
                    screenshot_path = self._capture_screenshot()
                    if screenshot_path:
                        self._process_screenshot(screenshot_path)
                
                time.sleep(min(60, config.SCREENSHOT_INTERVAL))  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in screenshot capture loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def _should_capture(self) -> bool:
        """Check if a screenshot should be captured"""
        if not self.last_capture_time:
            return True
        
        elapsed = (datetime.now() - self.last_capture_time).total_seconds()
        return elapsed >= config.SCREENSHOT_INTERVAL
    
    def _capture_screenshot(self) -> Optional[str]:
        """Capture a screenshot"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert RGBA to RGB if necessary (JPEG doesn't support transparency)
            if screenshot.mode == 'RGBA':
                # Create white background
                rgb_screenshot = Image.new('RGB', screenshot.size, (255, 255, 255))
                rgb_screenshot.paste(screenshot, mask=screenshot.split()[-1])  # Use alpha channel as mask
                screenshot = rgb_screenshot
            elif screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')
            
            # Resize if configured
            if config.SCREENSHOT_RESIZE:
                screenshot = screenshot.resize(config.SCREENSHOT_RESIZE, Image.Resampling.LANCZOS)
            
            # Add metadata overlay
            screenshot = self._add_metadata_overlay(screenshot)
            
            # Save with compression
            screenshot.save(filepath, "JPEG", quality=config.SCREENSHOT_QUALITY, optimize=True)
            
            self.last_capture_time = datetime.now()
            logger.debug(f"Screenshot captured: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def _add_metadata_overlay(self, image: Image.Image) -> Image.Image:
        """Add metadata overlay to screenshot"""
        try:
            # Create a copy to avoid modifying original
            img_with_overlay = image.copy()
            draw = ImageDraw.Draw(img_with_overlay)
            
            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Try to load a font, fall back to default
            try:
                font = ImageFont.truetype("Arial.ttf", 14)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position (bottom-right corner)
            text = f"Captured: {timestamp}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = img_with_overlay.width - text_width - 10
            y = img_with_overlay.height - text_height - 10
            
            # Draw background rectangle
            padding = 5
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0)  # Black background (no transparency for JPEG)
            )
            
            # Draw text
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            return img_with_overlay
            
        except Exception as e:
            logger.error(f"Failed to add metadata overlay: {e}")
            return image
    
    def _process_screenshot(self, screenshot_path: str):
        """Process captured screenshot"""
        try:
            # Get file info
            file_size = os.path.getsize(screenshot_path)
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "file_size": file_size,
                "file_path": screenshot_path,
                "time_entry_id": getattr(self, 'time_entry_id', None)
            }
            
            # Add to queue for upload
            self.screenshot_queue.append({
                "file_path": screenshot_path,
                "metadata": metadata
            })
            
            # Try to upload immediately if API client available
            if self.api_client:
                self._upload_screenshot(screenshot_path, metadata)
            
        except Exception as e:
            logger.error(f"Failed to process screenshot: {e}")
    
    def _upload_screenshot(self, file_path: str, metadata: Dict):
        """Upload screenshot to server"""
        try:
            if not self.api_client:
                logger.warning("No API client available for screenshot upload")
                return
            
            time_entry_id = metadata.get("time_entry_id")
            if not time_entry_id:
                logger.warning("No time entry ID for screenshot upload")
                return
            
            # Upload file
            employee_id = getattr(self.api_client, 'employee_id', 'unknown')
            response = self.api_client.upload_screenshot(
                employee_id=str(employee_id),
                time_entry_id=str(time_entry_id) if time_entry_id else None,
                file_path=file_path
            )
            
            if response:
                logger.info(f"Screenshot uploaded successfully: {file_path}")
                # Remove from queue
                self.screenshot_queue = [
                    item for item in self.screenshot_queue 
                    if item["file_path"] != file_path
                ]
                
                # Optionally delete local file after successful upload
                if hasattr(config, 'DELETE_AFTER_UPLOAD') and config.DELETE_AFTER_UPLOAD:
                    try:
                        os.remove(file_path)
                        logger.debug(f"Local screenshot deleted: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete local screenshot: {e}")
            
        except Exception as e:
            logger.error(f"Failed to upload screenshot: {e}")
    
    def capture_manual_screenshot(self, description: str = None) -> Optional[str]:
        """Capture a manual screenshot"""
        if not SCREENSHOT_AVAILABLE:
            logger.warning("Screenshot capture not available")
            return None
        
        try:
            screenshot_path = self._capture_screenshot()
            if screenshot_path:
                # Add description to metadata
                metadata = {
                    "timestamp": datetime.now().isoformat(),
                    "description": description or "Manual screenshot",
                    "manual": True,
                    "time_entry_id": getattr(self, 'time_entry_id', None)
                }
                
                self._process_screenshot(screenshot_path)
                logger.info(f"Manual screenshot captured: {screenshot_path}")
                
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Failed to capture manual screenshot: {e}")
            return None
    
    def get_screenshot_queue(self) -> List[Dict]:
        """Get pending screenshot uploads"""
        return self.screenshot_queue.copy()
    
    def retry_failed_uploads(self):
        """Retry failed screenshot uploads"""
        if not self.api_client:
            return
        
        failed_uploads = []
        for item in self.screenshot_queue:
            try:
                self._upload_screenshot(item["file_path"], item["metadata"])
            except Exception as e:
                logger.error(f"Retry upload failed: {e}")
                failed_uploads.append(item)
        
        self.screenshot_queue = failed_uploads
    
    def get_local_screenshots(self, limit: int = 50) -> List[Dict]:
        """Get list of local screenshots"""
        screenshots = []
        
        try:
            files = os.listdir(self.screenshots_dir)
            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            image_files.sort(reverse=True)  # Most recent first
            
            for filename in image_files[:limit]:
                filepath = os.path.join(self.screenshots_dir, filename)
                try:
                    stat = os.stat(filepath)
                    screenshots.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Error getting info for {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Error listing local screenshots: {e}")
        
        return screenshots
    
    def cleanup_old_screenshots(self, days_old: int = 30):
        """Clean up old local screenshots"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            files = os.listdir(self.screenshots_dir)
            
            for filename in files:
                filepath = os.path.join(self.screenshots_dir, filename)
                try:
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        logger.debug(f"Deleted old screenshot: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to delete {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Error cleaning up screenshots: {e}")
    
    def get_screenshot_stats(self) -> Dict:
        """Get screenshot statistics"""
        try:
            files = os.listdir(self.screenshots_dir)
            image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            total_size = 0
            for filename in image_files:
                filepath = os.path.join(self.screenshots_dir, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
            
            return {
                "total_screenshots": len(image_files),
                "total_size_mb": total_size / (1024 * 1024),
                "pending_uploads": len(self.screenshot_queue),
                "capturing": self.capturing,
                "last_capture": self.last_capture_time.isoformat() if self.last_capture_time else None
            }
            
        except Exception as e:
            logger.error(f"Error getting screenshot stats: {e}")
            return {}
    
    def set_api_client(self, api_client):
        """Set API client for uploads"""
        self.api_client = api_client
    
    def is_screenshot_available(self) -> bool:
        """Check if screenshot capture is available"""
        return SCREENSHOT_AVAILABLE and config.SCREENSHOT_ENABLED 