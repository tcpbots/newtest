"""
COMPLETE Premium Downloader v3.0 - WITH CLOUDFLARE BYPASS
Fixes all download issues including Cloudflare protection
"""

import asyncio
import logging
import os
import tempfile
import time
import subprocess
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
    """Complete premium media downloader with Cloudflare bypass"""
    
    def __init__(self):
        self.config = Config()
        self.session: Optional[aiohttp.ClientSession] = None
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
            'twitch.tv': '🟣 Twitch'
        }
        
    async def initialize(self):
        """Initialize premium downloader"""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.DOWNLOAD_TIMEOUT, connect=30)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=20)
            )
            
            # Setup yt-dlp with Cloudflare bypass
            self._setup_ytdl_with_bypass()
            
            logger.info("✅ Premium downloader initialized with Cloudflare bypass")
            
        except Exception as e:
            logger.error(f"❌ Downloader initialization failed: {e}")
            raise
    
    def _setup_ytdl_with_bypass(self):
        """Setup yt-dlp with Cloudflare bypass and premium settings"""
        try:
            ytdl_opts = {
                'outtmpl': os.path.join(self.config.TEMP_DIR, '%(title).100s.%(ext)s'),
                'restrictfilenames': True,
                'format': 'best[height<=2160]',
                
                # Cloudflare bypass settings
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
                },
                
                # Network settings
                'http_timeout': 120,
                'retries': 10,
                'fragment_retries': 15,
                'file_access_retries': 5,
                
                # Bypass settings
                'extractor_args': {
                    'generic': {
                        'impersonate': 'chrome-120'  # Cloudflare bypass
                    }
                },
                
                # Performance
                'concurrent_fragment_downloads': 4,
                'buffersize': 16384,
                
                # Other settings
                'noplaylist': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'quiet': False,
                'verbose': False
            }
            
            self.ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            logger.debug("✅ yt-dlp configured with Cloudflare bypass")
            
        except Exception as e:
            logger.error(f"❌ yt-dlp setup failed: {e}")
            raise
    
    def is_supported_platform(self, url: str) -> bool:
        """Check if URL is from supported platform"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '')
            return any(platform in domain for platform in self.supported_platforms.keys())
        except:
            return False
    
    def get_platform_name(self, url: str) -> str:
        """Get platform name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '')
            
            for platform, name in self.supported_platforms.items():
                if platform in domain:
                    return name.split(' ', 1)[1]
            return "Unknown Platform"
        except:
            return "Unknown Platform"
    
    def get_platform_emoji(self, url: str) -> str:
        """Get platform emoji from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '').replace('m.', '')
            
            for platform, name in self.supported_platforms.items():
                if platform in domain:
                    return name.split(' ')[0]
            return "🌐"
        except:
            return "🌐"
    
    async def get_supported_platforms_list(self) -> List[str]:
        """Get formatted list of supported platforms"""
        return [f"{name}" for name in self.supported_platforms.values()]
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information safely"""
        try:
            logger.info(f"📋 Extracting info for: {self.get_platform_name(url)}")
            
            loop = asyncio.get_event_loop()
            
            def extract_info():
                try:
                    info = self.ytdl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    logger.error(f"Info extraction error: {e}")
                    return None
            
            info = await loop.run_in_executor(None, extract_info)
            
            if not info:
                return {'success': False, 'error': 'Failed to extract video information'}
            
            result = {
                'success': True,
                'title': info.get('title', 'Unknown Title'),
                'platform': self.get_platform_name(url),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'formats': [],
                'audio_formats': []
            }
            
            if 'formats' in info and info['formats']:
                for fmt in info['formats']:
                    format_info = {
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'height': fmt.get('height'),
                        'filesize': fmt.get('filesize')
                    }
                    
                    if fmt.get('vcodec') != 'none' and fmt.get('height'):
                        result['formats'].append(format_info)
                    elif fmt.get('acodec') != 'none':
                        result['audio_formats'].append(format_info)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Video info extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_with_retry(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best',
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Download with enhanced retry logic"""
        
        max_retries = self.config.MAX_RETRIES
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                result = await self._download_single(
                    url, format_id, extract_audio, quality, progress_callback
                )
                
                if result['success']:
                    result['retry_count'] = attempt
                    return result
                
                logger.warning(f"⚠️ Attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} for {url}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                
            except Exception as e:
                logger.error(f"❌ Download attempt {attempt + 1} exception: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
        
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
        """Single download attempt with Cloudflare bypass"""
        
        start_time = time.time()
        
        try:
            # Try direct download first for simple URLs
            if not self.is_supported_platform(url):
                result = await self._download_direct(url, progress_callback)
                if result['success']:
                    return result
            
            # Use yt-dlp with Cloudflare bypass
            result = await self._download_ytdlp(url, format_id, extract_audio, quality, progress_callback)
            
            if result['success']:
                result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return {
                'success': False,
                'error': f'Download error: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    async def _download_direct(self, url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Direct download with progress tracking"""
        try:
            logger.info("📥 Starting direct download...")
            
            temp_file = tempfile.mktemp(suffix='.tmp', dir=self.config.TEMP_DIR)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {'success': False, 'error': f'HTTP {response.status}'}
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                
                async with aiofiles.open(temp_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            elapsed = time.time() - start_time
                            speed = downloaded / elapsed if elapsed > 0 else 0
                            progress = int((downloaded / total_size) * 100)
                            
                            try:
                                await progress_callback({
                                    'status': 'downloading',
                                    'progress': progress,
                                    'downloaded': downloaded,
                                    'total': total_size,
                                    'speed': speed
                                })
                            except:
                                pass
                
                return {
                    'success': True,
                    'filepath': temp_file,
                    'filename': os.path.basename(temp_file),
                    'filesize': downloaded,
                    'platform': 'Direct',
                    'quality': 'original'
                }
                
        except Exception as e:
            logger.error(f"❌ Direct download failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _download_ytdlp(
        self, 
        url: str, 
        format_id: Optional[str] = None,
        extract_audio: bool = False,
        quality: str = 'best',
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Download using yt-dlp with Cloudflare bypass"""
        try:
            logger.info("📥 Starting yt-dlp download with Cloudflare bypass...")
            
            def ytdl_progress_hook(d):
                if d['status'] == 'downloading' and progress_callback:
                    try:
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        
                        if total > 0:
                            progress = int((downloaded / total) * 100)
                            speed = d.get('speed', 0) or 0
                            
                            # Create task for async callback
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                loop.create_task(progress_callback({
                                    'status': 'downloading',
                                    'progress': progress,
                                    'downloaded': downloaded,
                                    'total': total,
                                    'speed': speed
                                }))
                    except:
                        pass
            
            # Configure format
            ytdl_opts = self.ytdl.params.copy()
            ytdl_opts['progress_hooks'] = [ytdl_progress_hook]
            
            if extract_audio:
                ytdl_opts['format'] = 'bestaudio/best'
            elif format_id:
                ytdl_opts['format'] = format_id
            else:
                format_map = {
                    'best': 'best[height<=2160]',
                    'balanced': 'best[height<=1080]', 
                    'fast': 'worst[height>=480]/worst'
                }
                ytdl_opts['format'] = format_map.get(quality, quality)
            
            # Download in executor
            loop = asyncio.get_event_loop()
            
            def download():
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        info = ytdl.extract_info(url, download=True)
                        return info
                except Exception as e:
                    logger.error(f"yt-dlp download error: {e}")
                    raise e
            
            info = await loop.run_in_executor(None, download)
            
            if not info:
                return {'success': False, 'error': 'yt-dlp returned no info'}
            
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
                title = info.get('title', 'video')[:50]
                safe_title = re.sub(r'[^\w\s-]', '', title).strip()
                
                temp_dir = Path(self.config.TEMP_DIR)
                for file_path in temp_dir.glob('*'):
                    if safe_title.lower() in file_path.name.lower():
                        downloaded_file = str(file_path)
                        break
            
            if not downloaded_file:
                return {'success': False, 'error': 'Downloaded file not found'}
            
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
                'format': info.get('ext', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ yt-dlp download failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close(self):
        """Close downloader resources"""
        try:
            if self.session:
                await self.session.close()
                logger.info("✅ HTTP session closed")
        except Exception as e:
            logger.error(f"❌ Error closing downloader: {e}")


# Global downloader instance
downloader = PremiumMediaDownloader()
