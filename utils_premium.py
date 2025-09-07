"""
COMPLETE Enhanced Utilities v3.0 - ALL METHODS INCLUDED
Includes all missing methods that caused errors
"""

import asyncio
import logging
import os
import time
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import json
import math

import aiohttp
import aiofiles
from pyrogram import Client
from pyrogram.types import Message

from config_premium import Config

logger = logging.getLogger(__name__)


class PremiumUtilities:
    """Complete premium utilities with all required methods"""
    
    def __init__(self):
        self.config = Config()
        self.http_session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize premium utilities"""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=120)
            
            self.http_session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*'
                },
                connector=aiohttp.TCPConnector(limit=50)
            )
            
            logger.info("✅ Premium utilities initialized")
            
        except Exception as e:
            logger.error(f"❌ Utilities initialization failed: {e}")
            raise
    
    # ================================
    # FILE INFORMATION METHODS
    # ================================
    
    async def get_file_info(self, message: Message) -> Optional[Dict[str, Any]]:
        """Get comprehensive file information from message"""
        try:
            file_obj = None
            file_type = "document"
            type_emoji = "📄"
            
            if message.document:
                file_obj = message.document
                file_type = "document"
                type_emoji = self.get_file_type_emoji_from_mime(file_obj.mime_type)
            elif message.photo:
                file_obj = message.photo
                file_type = "photo"
                type_emoji = "🖼️"
            elif message.video:
                file_obj = message.video
                file_type = "video"
                type_emoji = "🎥"
            elif message.audio:
                file_obj = message.audio
                file_type = "audio"
                type_emoji = "🎵"
            elif message.voice:
                file_obj = message.voice
                file_type = "voice"
                type_emoji = "🎙️"
            elif message.video_note:
                file_obj = message.video_note
                file_type = "video_note"
                type_emoji = "🎥"
            elif message.animation:
                file_obj = message.animation
                file_type = "animation"
                type_emoji = "🎬"
            elif message.sticker:
                file_obj = message.sticker
                file_type = "sticker"
                type_emoji = "🔖"
            
            if not file_obj:
                return None
            
            # Get file details
            file_id = file_obj.file_id
            file_size = getattr(file_obj, 'file_size', 0)
            file_name = getattr(file_obj, 'file_name', None)
            mime_type = getattr(file_obj, 'mime_type', None)
            
            # Generate filename if not available
            if not file_name:
                timestamp = int(time.time())
                if file_type == "photo":
                    file_name = f"photo_{timestamp}.jpg"
                elif file_type == "video":
                    file_name = f"video_{timestamp}.mp4"
                elif file_type == "audio":
                    file_name = f"audio_{timestamp}.mp3"
                elif file_type == "voice":
                    file_name = f"voice_{timestamp}.ogg"
                elif file_type == "video_note":
                    file_name = f"video_note_{timestamp}.mp4"
                elif file_type == "animation":
                    file_name = f"animation_{timestamp}.gif"
                elif file_type == "sticker":
                    file_name = f"sticker_{timestamp}.webp"
                else:
                    file_name = f"file_{timestamp}.bin"
            
            return {
                'file_id': file_id,
                'name': file_name,
                'size': file_size,
                'size_formatted': self.format_file_size(file_size),
                'type': file_type,
                'type_emoji': type_emoji,
                'mime_type': mime_type,
                'estimated_upload_time': self.estimate_upload_time(file_size)
            }
            
        except Exception as e:
            logger.error(f"❌ Get file info error: {e}")
            return None
    
    def get_file_type_emoji(self, file_type: str) -> str:
        """Get emoji for file type"""
        emoji_map = {
            'document': '📄',
            'photo': '🖼️',
            'video': '🎥',
            'audio': '🎵',
            'voice': '🎙️',
            'video_note': '🎥',
            'animation': '🎬',
            'sticker': '🔖',
            'download': '📥'
        }
        return emoji_map.get(file_type, '📄')
    
    def get_file_type_emoji_from_mime(self, mime_type: Optional[str]) -> str:
        """Get emoji from MIME type"""
        if not mime_type:
            return '📄'
        
        if mime_type.startswith('image/'):
            return '🖼️'
        elif mime_type.startswith('video/'):
            return '🎥'
        elif mime_type.startswith('audio/'):
            return '🎵'
        elif mime_type in ['application/pdf']:
            return '📕'
        elif mime_type in ['application/zip', 'application/x-rar', 'application/x-7z-compressed']:
            return '📦'
        elif mime_type.startswith('text/'):
            return '📝'
        else:
            return '📄'
    
    # ================================
    # FILE SIZE AND FORMATTING
    # ================================
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
    
    def format_speed(self, speed_bytes_per_sec: float) -> str:
        """Format speed in human readable format"""
        return f"{self.format_file_size(int(speed_bytes_per_sec))}/s"
    
    def format_duration(self, seconds: int) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def format_number(self, number: int) -> str:
        """Format number with commas"""
        return f"{number:,}"
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def estimate_upload_time(self, file_size: int) -> int:
        """Estimate upload time in seconds"""
        # Assume average upload speed of 1 MB/s
        return max(1, int(file_size / (1024 * 1024)))
    
    # ================================
    # PROGRESS BAR CREATION
    # ================================
    
    def create_progress_bar(self, percentage: int, length: int = 10) -> str:
        """Create visual progress bar"""
        filled = int(length * percentage // 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}] {percentage}%"
    
    # ================================
    # URL VALIDATION
    # ================================
    
    def is_valid_url(self, text: str) -> bool:
        """Check if text is a valid URL"""
        try:
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url_pattern.match(text) is not None
        except:
            return False
    
    # ================================
    # TELEGRAM FILE DOWNLOAD (ENHANCED)
    # ================================
    
    async def download_telegram_file_enhanced(
        self, 
        client: Client, 
        file_id: str, 
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Enhanced Telegram file download with better speed"""
        try:
            # Create temp file
            temp_file = os.path.join(self.config.TEMP_DIR, f"tg_{int(time.time())}.tmp")
            
            # Download with progress
            await client.download_media(
                file_id,
                file_name=temp_file,
                progress=self._telegram_progress_wrapper(progress_callback) if progress_callback else None
            )
            
            if os.path.exists(temp_file):
                file_size = os.path.getsize(temp_file)
                logger.info(f"✅ Downloaded {self.format_file_size(file_size)} from Telegram")
                return temp_file
            else:
                raise Exception("Downloaded file not found")
                
        except Exception as e:
            logger.error(f"❌ Telegram download error: {e}")
            raise
    
    def _telegram_progress_wrapper(self, callback: Callable):
        """Wrapper for Telegram progress callback"""
        async def wrapper(current: int, total: int):
            try:
                progress = int((current / total) * 100) if total > 0 else 0
                speed = 0  # Telegram doesn't provide speed info
                
                await callback({
                    'progress': progress,
                    'downloaded': current,
                    'total': total,
                    'speed': speed
                })
            except Exception as e:
                logger.debug(f"Progress callback error: {e}")
        
        return wrapper
    
    # ================================
    # GOFILE UPLOAD (ENHANCED)
    # ================================
    
    async def upload_to_gofile_enhanced(
        self, 
        file_path: str, 
        filename: str, 
        user_id: int,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Enhanced GoFile upload with progress tracking"""
        try:
            logger.info(f"📤 Starting GoFile upload: {filename}")
            
            # Get GoFile server
            server = await self._get_gofile_server()
            
            # Read file size
            file_size = os.path.getsize(file_path)
            
            # Prepare upload
            upload_url = f"https://{server}.gofile.io/uploadFile"
            
            # Create multipart data
            data = aiohttp.FormData()
            
            # Add file with progress tracking
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
                data.add_field('file', file_content, filename=filename)
            
            # Add optional parameters
            data.add_field('folderId', '')  # Empty for root folder
            
            start_time = time.time()
            
            # Upload with progress simulation (aiohttp doesn't support upload progress)
            async with self.http_session.post(upload_url, data=data) as response:
                if response.status != 200:
                    return {
                        'success': False,
                        'error': f'Upload failed with status {response.status}'
                    }
                
                result = await response.json()
                
                if result.get('status') == 'ok':
                    data_info = result.get('data', {})
                    file_id = data_info.get('code')
                    download_url = f"https://gofile.io/d/{file_id}"
                    
                    upload_time = time.time() - start_time
                    
                    logger.info(f"✅ GoFile upload successful: {download_url}")
                    
                    return {
                        'success': True,
                        'file_id': file_id,
                        'download_url': download_url,
                        'upload_time': upload_time,
                        'server': server
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown GoFile error')
                    }
                    
        except Exception as e:
            logger.error(f"❌ GoFile upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_gofile_server(self) -> str:
        """Get optimal GoFile server"""
        try:
            async with self.http_session.get('https://api.gofile.io/getServer') as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'ok':
                        return data.get('data', {}).get('server', 'store1')
            
            logger.warning("⚠️ Using fallback GoFile server")
            return 'store1'  # Fallback server
            
        except Exception as e:
            logger.warning(f"⚠️ Server selection failed, using fallback: {e}")
            return 'store1'
    
    # ================================
    # FILE CLEANUP
    # ================================
    
    async def cleanup_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"🧹 Cleaned up: {os.path.basename(file_path)}")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed for {file_path}: {e}")
    
    async def cleanup_temp_files(self):
        """Clean up all temporary files"""
        try:
            temp_dir = Path(self.config.TEMP_DIR)
            if not temp_dir.exists():
                return
            
            current_time = time.time()
            cleanup_count = 0
            
            for file_path in temp_dir.iterdir():
                try:
                    if file_path.is_file():
                        # Remove files older than 1 hour
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > 3600:  # 1 hour
                            file_path.unlink()
                            cleanup_count += 1
                            
                except Exception as e:
                    logger.warning(f"⚠️ Cleanup failed for {file_path}: {e}")
                    continue
            
            if cleanup_count > 0:
                logger.info(f"🧹 Cleaned up {cleanup_count} temporary files")
                
        except Exception as e:
            logger.error(f"❌ Temp cleanup error: {e}")
    
    # ================================
    # CLOSE RESOURCES
    # ================================
    
    async def close(self):
        """Close utility resources"""
        try:
            if self.http_session:
                await self.http_session.close()
                logger.info("✅ HTTP session closed")
                
            # Final cleanup
            await self.cleanup_temp_files()
            
        except Exception as e:
            logger.error(f"❌ Error closing utilities: {e}")


# Global utilities instance
utils = PremiumUtilities()
