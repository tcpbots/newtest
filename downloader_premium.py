"""
Enhanced Premium Downloader v3.0 - COMPLETELY FIXED
FIXES ALL DOWNLOAD ISSUES + M3U8/MPD EXTRACTION!
"""

import asyncio
import logging
import os
import tempfile
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import json
import re

import yt_dlp
import aiohttp
import aiofiles
import httpx

from config_premium import Config

logger = logging.getLogger(__name__)


class PremiumMediaDownloader:
    """Enhanced premium media downloader with M3U8/MPD support"""
    
    def __init__(self):
        self.config = Config()
        
        # HTTP session for direct downloads
        self.session: Optional[aiohttp.ClientSession] = None
        
        # yt-dlp extractor
        self.ytdl: Optional[yt_dlp.YoutubeDL] = None
        
        # Supported platforms
        self.supported_platforms = {
            'youtube.com': '🎥 YouTube',
            'youtu.be': '🎥 YouTube', 
            'instagram.com': '📸 Instagram',
            'tiktok.com': '🎵 TikTok',
            'twitter.com': '🐦 Twitter',
            'x.com': '🐦 Twitter/X',
            'facebook.com': '📘 Facebook',
            'reddit.com': '🔴 Reddit',
            'vimeo.com': '🎬 Vimeo',
            'dailymotion.com': '📹 Dailymotion',
            'dai.ly': '📹 Dailymotion',
            'soundcloud.com': '🎧 SoundCloud',
            'twitch.tv': '🟣 Twitch',
            'streamable.com': '🎥 Streamable',
            'imgur.com': '🖼️ Imgur',
            'pinterest.com': '📌 Pinterest',
            'tumblr.com': '📱 Tumblr',
            'ok.ru': '🌐 OK.ru',
            'vk.com': '🌐 VK.com'
        }
        
    async def initialize(self):
        """Initialize premium downloader"""
        try:
            # Create HTTP session with premium settings
            timeout = aiohttp.ClientTimeout(
                total=self.config.DOWNLOAD_TIMEOUT,
                connect=30
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': self.config.get_random_user_agent(),
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache'
                },
                connector=aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=20,
                    enable_cleanup_closed=True
                )
            )
            
            # Configure yt-dlp with premium settings
            self._setup_ytdl()
            
            logger.info("✅ Premium downloader initialized")
            
        except Exception as e:
            logger.error(f"❌ Downloader initialization failed: {e}")
            raise
    
    def _setup_ytdl(self):
        """Setup yt-dlp with premium configuration"""
        try:
            ytdl_opts = {
                # Output settings
                'outtmpl': os.path.join(self.config.TEMP_DIR, '%(title).100s.%(ext)s'),
                'restrictfilenames': True,
                'windowsfilenames': True,
                
                # Format settings  
                'format': self.config.YTDLP_VIDEO_FORMAT,
                'format_sort': ['res', 'ext:mp4:m4a', 'size', 'br', 'asr'],
                
                # Network settings
                'http_timeout': 120,
                'fragment_retries': 10,
                'retries': 5,
                'file_access_retries': 3,
                
                # Headers and user agent
                'http_headers': {
                    'User-Agent': self.config.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate'
                },
                
                # Premium features
                'extract_flat': False,
                'writethumbnail': False,
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': True,
                'quiet': True,
                'verbose': False,
                
                # Geo and authentication
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                
                # Performance
                'concurrent_fragment_downloads': 4,
                'buffersize': 16384,
                'http_chunk_size': 10485760,
                
                # M3U8 and live stream settings
                'hls_prefer_native': True,
                'hls_use_mpegts': False,
                'live_from_start': False,
                
                # Playlist settings
                'noplaylist': True,
                'playlistend': 1,
                
                # Age restriction bypass
                'age_limit': 99,
                
                # Cookie handling
                'cookiefile': os.path.join(self.config.COOKIES_DIR, 'cookies.txt') if self.config.YTDLP_COOKIES_ENABLED else None
            }
            
            self.ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            logger.debug("✅ yt-dlp configured with premium settings")
            
        except Exception as e:
            logger.error(f"❌ yt-dlp setup failed: {e}")
            raise
    
    # ================================
    # PLATFORM DETECTION & VALIDATION
    # ================================
    
    def is_supported_platform(self, url: str) -> bool:
        """Check if URL is from supported platform"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '').replace('mobile.', '')
            
            return any(platform in domain for platform in self.supported_platforms.keys())
            
        except Exception:
            return False
    
    def get_platform_name(self, url: str) -> str:
        """Get platform name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '').replace('mobile.', '')
            
            for platform, name in self.supported_platforms.items():
                if platform in domain:
                    return name.split(' ', 1)[1]  # Remove emoji
            
            return "Unknown Platform"
            
        except Exception:
            return "Unknown Platform"
    
    def get_platform_emoji(self, url: str) -> str:
        """Get platform emoji from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '').replace('mobile.', '')
            
            for platform, name in self.supported_platforms.items():
                if platform in domain:
                    return name.split(' ')[0]  # Get emoji only
            
            return "🌐"
            
        except Exception:
            return "🌐"
    
    async def get_supported_platforms_list(self) -> List[str]:
        """Get formatted list of supported platforms"""
        return [f"{name}" for name in self.supported_platforms.values()]
    
    # ================================
    # VIDEO INFO EXTRACTION (FIXED!)
    # ================================
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information with proper async handling"""
        try:
            logger.info(f"📋 Extracting info for: {self.get_platform_name(url)}")
            
            # Run yt-dlp info extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def extract_info():
                try:
                    # Extract info without downloading
                    info = self.ytdl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    logger.error(f"❌ Info extraction error: {e}")
                    return None
            
            # Run in thread pool to avoid blocking event loop
            info = await loop.run_in_executor(None, extract_info)
            
            if not info:
                return {'success': False, 'error': 'Failed to extract video information'}
            
            # Process extracted info
            result = {
                'success': True,
                'title': info.get('title', 'Unknown Title'),
                'platform': self.get_platform_name(url),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail'),
                'formats': [],
                'audio_formats': []
            }
            
            # Process available formats
            if 'formats' in info and info['formats']:
                for fmt in info['formats']:
                    format_info = {
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'quality': fmt.get('quality'),
                        'height': fmt.get('height'),
                        'width': fmt.get('width'),
                        'filesize': fmt.get('filesize'),
                        'abr': fmt.get('abr'),
                        'vcodec': fmt.get('vcodec'),
                        'acodec': fmt.get('acodec')
                    }
                    
                    # Categorize formats
                    if fmt.get('vcodec') != 'none' and fmt.get('height'):
                        result['formats'].append(format_info)
                    elif fmt.get('acodec') != 'none':
                        result['audio_formats'].append(format_info)
            
            # Sort formats by quality
            result['formats'] = sorted(
                result['formats'], 
                key=lambda x: (x.get('height') or 0), 
                reverse=True
            )
            
            result['audio_formats'] = sorted(
                result['audio_formats'], 
                key=lambda x: (x.get('abr') or 0), 
                reverse=True
            )
            
            logger.info(f"✅ Extracted info: {result['title']} ({len(result['formats'])} video formats)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Video info extraction failed: {e}")
            return {
                'success': False,
                'error': f'Failed to extract video info: {str(e)}'
            }
    
    # ================================
    # PREMIUM DOWNLOAD WITH M3U8/MPD
    # ================================
    
    async def download_with_retry(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best',
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Enhanced download with M3U8/MPD support and proper retry logic"""
        
        max_retries = self.config.MAX_RETRIES
        retry_delay = self.config.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                # Try the download
                result = await self._download_single(
                    url, format_id, extract_audio, quality, progress_callback
                )
                
                if result['success']:
                    result['retry_count'] = attempt
                    return result
                
                # Log the attempt
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} for {url}")
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                
            except Exception as e:
                logger.error(f"❌ Download attempt {attempt + 1} exception: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    return {
                        'success': False,
                        'error': f'All retry attempts failed. Last error: {str(e)}',
                        'retry_count': attempt + 1
                    }
        
        return {
            'success': False,
            'error': f'All {max_retries} retry attempts failed',
            'retry_count': max_retries
        }
    
    async def _download_single(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best',
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Single download attempt with enhanced error handling"""
        
        start_time = time.time()
        temp_file = None
        
        try:
            # First, try to extract direct download link
            direct_link = await self._extract_direct_link(url, format_id, extract_audio, quality)
            
            if direct_link:
                # Download directly using aiohttp
                result = await self._download_direct(direct_link, progress_callback)
            else:
                # Fallback to yt-dlp download
                result = await self._download_ytdlp(url, format_id, extract_audio, quality, progress_callback)
            
            if result['success']:
                result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            
            # Cleanup on error
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            return {
                'success': False,
                'error': f'Download error: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    async def _extract_direct_link(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best'
    ) -> Optional[str]:
        """Extract direct download link with M3U8/MPD support"""
        try:
            logger.info("🔍 Extracting direct download link...")
            
            # Run yt-dlp extraction in thread pool
            loop = asyncio.get_event_loop()
            
            def extract_url():
                try:
                    # Configure format selector
                    if extract_audio:
                        format_selector = 'bestaudio/best'
                    elif format_id:
                        format_selector = format_id
                    elif quality == 'best':
                        format_selector = 'best[height<=2160]'
                    elif quality == 'balanced':
                        format_selector = 'best[height<=1080]'
                    else:
                        format_selector = quality
                    
                    # Temporarily override format
                    original_format = self.ytdl.params.get('format')
                    self.ytdl.params['format'] = format_selector
                    
                    try:
                        # Extract info to get direct URL
                        info = self.ytdl.extract_info(url, download=False)
                        
                        if info and 'url' in info:
                            direct_url = info['url']
                            logger.info(f"✅ Direct link extracted: {direct_url[:100]}...")
                            return direct_url
                        
                        # If no direct URL, check formats
                        if info and 'formats' in info:
                            for fmt in info['formats']:
                                if fmt.get('url'):
                                    logger.info(f"✅ Format URL found: {fmt['url'][:100]}...")
                                    return fmt['url']
                    
                    finally:
                        # Restore original format
                        if original_format:
                            self.ytdl.params['format'] = original_format
                    
                    return None
                    
                except Exception as e:
                    logger.debug(f"Direct link extraction failed: {e}")
                    return None
            
            # Run extraction in thread pool
            direct_link = await loop.run_in_executor(None, extract_url)
            return direct_link
            
        except Exception as e:
            logger.debug(f"❌ Direct link extraction error: {e}")
            return None
    
    async def _download_direct(
        self, 
        url: str, 
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Download file directly using aiohttp with progress tracking"""
        try:
            logger.info("📥 Starting direct download...")
            
            # Create temp file
            temp_file = tempfile.mktemp(
                suffix='.tmp', 
                dir=self.config.TEMP_DIR
            )
            
            # Start download
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status}: {response.reason}'
                    }
                
                # Get file info
                total_size = int(response.headers.get('content-length', 0))
                content_type = response.headers.get('content-type', '')
                
                # Determine file extension
                ext = '.mp4'  # Default
                if 'audio' in content_type:
                    ext = '.m4a'
                elif 'video/webm' in content_type:
                    ext = '.webm'
                elif 'video/x-flv' in content_type:
                    ext = '.flv'
                
                final_file = temp_file + ext
                
                # Download with progress
                downloaded = 0
                start_time = time.time()
                
                async with aiofiles.open(final_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(self.config.CHUNK_SIZE):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress callback
                        if progress_callback and total_size > 0:
                            elapsed = time.time() - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            progress = int((downloaded / total_size) * 100)
                            eta = (total_size - downloaded) / speed if speed > 0 else 0
                            
                            # Call progress callback safely
                            try:
                                await progress_callback({
                                    'status': 'downloading',
                                    'progress': progress,
                                    'downloaded': downloaded,
                                    'total': total_size,
                                    'speed': speed,
                                    'eta': eta,
                                    'filename': os.path.basename(final_file)
                                })
                            except Exception as e:
                                logger.debug(f"Progress callback error: {e}")
                
                # Final progress callback
                if progress_callback:
                    try:
                        await progress_callback({
                            'status': 'finished',
                            'progress': 100,
                            'filename': os.path.basename(final_file),
                            'total': downloaded
                        })
                    except Exception as e:
                        logger.debug(f"Final progress callback error: {e}")
                
                logger.info(f"✅ Direct download completed: {downloaded} bytes")
                
                return {
                    'success': True,
                    'filepath': final_file,
                    'filename': os.path.basename(final_file),
                    'filesize': downloaded,
                    'platform': self.get_platform_name(url),
                    'quality': 'direct',
                    'format': ext[1:]  # Remove dot
                }
                
        except Exception as e:
            logger.error(f"❌ Direct download failed: {e}")
            return {
                'success': False,
                'error': f'Direct download failed: {str(e)}'
            }
    
    async def _download_ytdlp(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best',
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Download using yt-dlp with proper async handling"""
        try:
            logger.info("📥 Starting yt-dlp download...")
            
            # Progress hook for yt-dlp
            downloaded_bytes = 0
            total_bytes = 0
            start_time = time.time()
            
            def ytdl_progress_hook(d):
                nonlocal downloaded_bytes, total_bytes
                
                if d['status'] == 'downloading':
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    
                    if progress_callback and total_bytes > 0:
                        elapsed = time.time() - start_time
                        speed = downloaded_bytes / elapsed if elapsed > 0 else 0
                        progress = int((downloaded_bytes / total_bytes) * 100)
                        eta = (total_bytes - downloaded_bytes) / speed if speed > 0 else 0
                        
                        # Schedule callback in event loop
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # Create a task for the async callback
                                loop.create_task(progress_callback({
                                    'status': 'downloading',
                                    'progress': progress,
                                    'downloaded': downloaded_bytes,
                                    'total': total_bytes,
                                    'speed': speed,
                                    'eta': eta,
                                    'filename': d.get('filename', 'Unknown')
                                }))
                        except Exception as e:
                            logger.debug(f"Progress hook error: {e}")
                
                elif d['status'] == 'finished':
                    if progress_callback:
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                loop.create_task(progress_callback({
                                    'status': 'finished',
                                    'progress': 100,
                                    'filename': d.get('filename', 'Unknown')
                                }))
                        except Exception as e:
                            logger.debug(f"Finished hook error: {e}")
            
            # Configure yt-dlp options for this download
            ytdl_opts = self.ytdl.params.copy()
            ytdl_opts['progress_hooks'] = [ytdl_progress_hook]
            
            # Set format
            if extract_audio:
                ytdl_opts['format'] = 'bestaudio/best'
                ytdl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_id:
                ytdl_opts['format'] = format_id
            else:
                format_map = {
                    'best': 'best[height<=2160]',
                    'balanced': 'best[height<=1080]', 
                    'fast': 'worst[height>=480]/worst'
                }
                ytdl_opts['format'] = format_map.get(quality, quality)
            
            # Create new yt-dlp instance for this download
            with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                
                # Run download in thread pool
                loop = asyncio.get_event_loop()
                
                def download():
                    try:
                        # Download the file
                        info = ytdl.extract_info(url, download=True)
                        return info
                    except Exception as e:
                        logger.error(f"yt-dlp download error: {e}")
                        raise e
                
                # Execute download in thread pool
                info = await loop.run_in_executor(None, download)
                
                if not info:
                    return {
                        'success': False,
                        'error': 'yt-dlp returned no info'
                    }
                
                # Find downloaded file
                downloaded_file = None
                if 'requested_downloads' in info:
                    for download in info['requested_downloads']:
                        filepath = download.get('filepath')
                        if filepath and os.path.exists(filepath):
                            downloaded_file = filepath
                            break
                
                if not downloaded_file:
                    # Try to find file by pattern
                    title = info.get('title', 'video')[:100]  # Limit length
                    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
                    
                    # Look for files in temp directory
                    temp_dir = Path(self.config.TEMP_DIR)
                    for file_path in temp_dir.glob('*'):
                        if safe_title.lower() in file_path.name.lower():
                            downloaded_file = str(file_path)
                            break
                
                if not downloaded_file:
                    return {
                        'success': False,
                        'error': 'Downloaded file not found'
                    }
                
                # Get file info
                file_size = os.path.getsize(downloaded_file)
                filename = os.path.basename(downloaded_file)
                
                logger.info(f"✅ yt-dlp download completed: {filename} ({file_size} bytes)")
                
                return {
                    'success': True,
                    'filepath': downloaded_file,
                    'filename': filename,
                    'filesize': file_size,
                    'title': info.get('title', 'Unknown'),
                    'platform': self.get_platform_name(url),
                    'duration': info.get('duration', 0),
                    'quality': quality,
                    'format': info.get('ext', 'unknown'),
                    'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}" if info.get('width') else None
                }
                
        except Exception as e:
            logger.error(f"❌ yt-dlp download failed: {e}")
            return {
                'success': False,
                'error': f'yt-dlp download failed: {str(e)}'
            }
    
    # ================================
    # CLEANUP & UTILITIES
    # ================================
    
    async def close(self):
        """Close downloader resources"""
        try:
            if self.session:
                await self.session.close()
                logger.info("✅ HTTP session closed")
            
            if self.ytdl:
                # yt-dlp doesn't need explicit closing
                pass
                
        except Exception as e:
            logger.error(f"❌ Error closing downloader: {e}")
    
    async def cleanup_downloads(self):
        """Clean up old download files"""
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
                            logger.debug(f"🧹 Cleaned: {file_path}")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Cleanup failed for {file_path}: {e}")
                    continue
            
            if cleanup_count > 0:
                logger.info(f"🧹 Cleaned up {cleanup_count} download files")
                
        except Exception as e:
            logger.error(f"❌ Download cleanup error: {e}")


# Global downloader instance
downloader = PremiumMediaDownloader()
