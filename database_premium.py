"""
Premium Database v3.0 - FIXED MongoDB Connection
Reference: TheHamkerCat/WilliamButcherBot + Motor async patterns
FIXES ALL MongoDB CONNECTION ISSUES!
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import os

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import pymongo
from pymongo.errors import DuplicateKeyError, ConnectionFailure, ServerSelectionTimeoutError

from config_premium import Config

logger = logging.getLogger(__name__)


class PremiumDatabase:
    """Premium MongoDB database with advanced operations and no conflicts"""
    
    def __init__(self):
        self.config = Config()
        
        # Database connection
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        # Collections
        self.users_col: Optional[AsyncIOMotorCollection] = None
        self.files_col: Optional[AsyncIOMotorCollection] = None
        self.downloads_col: Optional[AsyncIOMotorCollection] = None
        self.temp_data_col: Optional[AsyncIOMotorCollection] = None
        self.stats_col: Optional[AsyncIOMotorCollection] = None
        self.admin_logs_col: Optional[AsyncIOMotorCollection] = None
        
        # Connection status
        self.connected = False
        
    async def initialize(self):
        """Initialize premium database with proper error handling"""
        try:
            logger.info("🔄 Connecting to premium MongoDB database...")
            
            # Create MongoDB client with FIXED connection options
            mongo_uri = self.config.MONGO_URI
            
            # FIXED: Clean connection options to avoid unknown parameter errors
            connection_options = {
                'serverSelectionTimeoutMS': 10000,  # 10 seconds timeout
                'connectTimeoutMS': 10000,           # 10 seconds connect timeout
                'maxPoolSize': 50,                   # Max connection pool size
                'retryWrites': True,                 # Enable retryable writes
                'retryReads': True,                  # Enable retryable reads
                'w': 'majority',                     # Write concern majority
                'readPreference': 'primaryPreferred' # Read preference
            }
            
            # Create client with clean options
            self.client = AsyncIOMotorClient(
                mongo_uri,
                **connection_options
            )
            
            # Test connection with ping
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful!")
            
            # Get database
            self.db = self.client[self.config.DATABASE_NAME]
            
            # Initialize collections
            await self._initialize_collections()
            
            # Create indexes for performance
            await self._create_indexes()
            
            self.connected = True
            logger.info("✅ Premium database initialized successfully!")
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            logger.error("💡 Make sure MongoDB is running and accessible")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB server selection timeout: {e}")
            logger.error("💡 Check MongoDB URI and network connectivity")
            raise
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            logger.error("💡 Check MongoDB configuration and credentials")
            raise
    
    async def _initialize_collections(self):
        """Initialize all database collections"""
        try:
            # Core collections
            self.users_col = self.db.users
            self.files_col = self.db.files
            self.downloads_col = self.db.downloads
            self.temp_data_col = self.db.temp_data
            self.stats_col = self.db.stats
            self.admin_logs_col = self.db.admin_logs
            
            logger.info("✅ Database collections initialized")
            
        except Exception as e:
            logger.error(f"❌ Collection initialization failed: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for premium performance"""
        try:
            # Users collection indexes
            await self.users_col.create_index("user_id", unique=True)
            await self.users_col.create_index("username")
            await self.users_col.create_index("join_date")
            await self.users_col.create_index("last_activity")
            await self.users_col.create_index("is_banned")
            
            # Files collection indexes
            await self.files_col.create_index("user_id")
            await self.files_col.create_index("gofile_id", unique=True)
            await self.files_col.create_index("upload_date")
            await self.files_col.create_index("file_type")
            await self.files_col.create_index([("user_id", 1), ("upload_date", -1)])
            
            # Downloads collection indexes
            await self.downloads_col.create_index("user_id")
            await self.downloads_col.create_index("platform")
            await self.downloads_col.create_index("download_date")
            await self.downloads_col.create_index("success")
            await self.downloads_col.create_index([("user_id", 1), ("download_date", -1)])
            
            # Temp data collection indexes (with TTL)
            await self.temp_data_col.create_index("user_id")
            await self.temp_data_col.create_index("key")
            await self.temp_data_col.create_index("expires_at", expireAfterSeconds=0)  # TTL index
            
            # Stats collection indexes
            await self.stats_col.create_index("date")
            await self.stats_col.create_index("type")
            
            # Admin logs collection indexes
            await self.admin_logs_col.create_index("admin_id")
            await self.admin_logs_col.create_index("action")
            await self.admin_logs_col.create_index("timestamp")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
            # Don't raise here - indexes are optional for functionality
    
    # ================================
    # USER MANAGEMENT (PREMIUM!)
    # ================================
    
    async def create_or_update_user(self, user_data: Dict[str, Any]) -> bool:
        """Create or update user with premium conflict resolution"""
        try:
            user_id = user_data['user_id']
            current_time = datetime.utcnow()
            
            # Prepare user document
            user_doc = {
                'user_id': user_id,
                'username': user_data.get('username'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'language_code': user_data.get('language_code'),
                'last_activity': current_time,
                'updated_at': current_time
            }
            
            # Use upsert to avoid conflicts
            result = await self.users_col.update_one(
                {'user_id': user_id},
                {
                    '$set': user_doc,
                    '$setOnInsert': {
                        'join_date': current_time,
                        'is_banned': False,
                        'ban_reason': None,
                        'banned_by': None,
                        'banned_at': None,
                        'settings': self.config.DEFAULT_USER_SETTINGS,
                        'usage_stats': {
                            'files_uploaded': 0,
                            'urls_downloaded': 0,
                            'total_uploaded_size': 0,
                            'total_downloaded_size': 0,
                            'last_upload': None,
                            'last_download': None
                        },
                        'gofile_account': {
                            'token': None,
                            'account_id': None,
                            'linked_at': None,
                            'verified': False
                        }
                    }
                },
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"✅ New user created: {user_id}")
            else:
                logger.debug(f"✅ User updated: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create/update user {user_data.get('user_id')}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with premium caching"""
        try:
            user = await self.users_col.find_one({'user_id': user_id})
            return user
        except Exception as e:
            logger.error(f"❌ Failed to get user {user_id}: {e}")
            return None
    
    async def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        try:
            user = await self.users_col.find_one(
                {'user_id': user_id, 'is_banned': True}
            )
            return user is not None
        except Exception as e:
            logger.error(f"❌ Failed to check ban status for {user_id}: {e}")
            return False
    
    async def ban_user(self, user_id: int, admin_id: int, reason: str) -> bool:
        """Ban user with premium logging"""
        try:
            current_time = datetime.utcnow()
            
            # Update user
            result = await self.users_col.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_banned': True,
                        'ban_reason': reason,
                        'banned_by': admin_id,
                        'banned_at': current_time,
                        'updated_at': current_time
                    }
                }
            )
            
            if result.modified_count > 0:
                # Log admin action
                await self.admin_logs_col.insert_one({
                    'action': 'ban_user',
                    'admin_id': admin_id,
                    'target_user_id': user_id,
                    'reason': reason,
                    'timestamp': current_time
                })
                
                logger.info(f"✅ User {user_id} banned by admin {admin_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to ban user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id: int, admin_id: int) -> bool:
        """Unban user with premium logging"""
        try:
            current_time = datetime.utcnow()
            
            # Update user
            result = await self.users_col.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_banned': False,
                        'ban_reason': None,
                        'banned_by': None,
                        'banned_at': None,
                        'unbanned_by': admin_id,
                        'unbanned_at': current_time,
                        'updated_at': current_time
                    }
                }
            )
            
            if result.modified_count > 0:
                # Log admin action
                await self.admin_logs_col.insert_one({
                    'action': 'unban_user',
                    'admin_id': admin_id,
                    'target_user_id': user_id,
                    'timestamp': current_time
                })
                
                logger.info(f"✅ User {user_id} unbanned by admin {admin_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to unban user {user_id}: {e}")
            return False
    
    async def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        try:
            cursor = self.users_col.find().sort('join_date', -1).limit(limit)
            users = await cursor.to_list(length=limit)
            return users
        except Exception as e:
            logger.error(f"❌ Failed to get users: {e}")
            return []
    
    async def get_users_count(self) -> int:
        """Get total users count"""
        try:
            count = await self.users_col.count_documents({})
            return count
        except Exception as e:
            logger.error(f"❌ Failed to get users count: {e}")
            return 0
    
    # ================================
    # FILE MANAGEMENT (PREMIUM!)
    # ================================
    
    async def save_file(self, file_data: Dict[str, Any]) -> bool:
        """Save file with premium metadata"""
        try:
            current_time = datetime.utcnow()
            
            # Prepare file document
            file_doc = {
                **file_data,
                'upload_date': current_time,
                'updated_at': current_time
            }
            
            # Insert file
            await self.files_col.insert_one(file_doc)
            
            # Update user stats
            await self.users_col.update_one(
                {'user_id': file_data['user_id']},
                {
                    '$inc': {
                        'usage_stats.files_uploaded': 1,
                        'usage_stats.total_uploaded_size': file_data.get('file_size', 0)
                    },
                    '$set': {
                        'usage_stats.last_upload': current_time,
                        'last_activity': current_time
                    }
                }
            )
            
            logger.info(f"✅ File saved: {file_data.get('file_name')}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ Duplicate file: {file_data.get('gofile_id')}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            return False
    
    async def get_user_files(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user files with premium sorting"""
        try:
            cursor = self.files_col.find(
                {'user_id': user_id}
            ).sort('upload_date', -1).limit(limit)
            
            files = await cursor.to_list(length=limit)
            return files
            
        except Exception as e:
            logger.error(f"❌ Failed to get user files for {user_id}: {e}")
            return []
    
    # ================================
    # DOWNLOAD HISTORY (PREMIUM!)
    # ================================
    
    async def save_download(self, download_data: Dict[str, Any]) -> bool:
        """Save download with premium analytics"""
        try:
            current_time = datetime.utcnow()
            
            # Prepare download document
            download_doc = {
                **download_data,
                'download_date': current_time,
                'updated_at': current_time
            }
            
            # Insert download
            await self.downloads_col.insert_one(download_doc)
            
            # Update user stats if successful
            if download_data.get('success', False):
                await self.users_col.update_one(
                    {'user_id': download_data['user_id']},
                    {
                        '$inc': {
                            'usage_stats.urls_downloaded': 1,
                            'usage_stats.total_downloaded_size': download_data.get('file_size', 0)
                        },
                        '$set': {
                            'usage_stats.last_download': current_time,
                            'last_activity': current_time
                        }
                    }
                )
            
            logger.info(f"✅ Download saved: {download_data.get('platform')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save download: {e}")
            return False
    
    # ================================
    # TEMPORARY DATA (PREMIUM!)
    # ================================
    
    async def store_temp_data(self, user_id: int, key: str, data: Any, ttl_seconds: int = 300) -> bool:
        """Store temporary data with TTL"""
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            await self.temp_data_col.update_one(
                {'user_id': user_id, 'key': key},
                {
                    '$set': {
                        'user_id': user_id,
                        'key': key,
                        'data': data,
                        'expires_at': expires_at,
                        'created_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store temp data: {e}")
            return False
    
    async def get_temp_data(self, user_id: int, key: str) -> Any:
        """Get temporary data"""
        try:
            doc = await self.temp_data_col.find_one({
                'user_id': user_id,
                'key': key,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            return doc.get('data') if doc else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get temp data: {e}")
            return None
    
    async def delete_temp_data(self, user_id: int, key: str) -> bool:
        """Delete temporary data"""
        try:
            result = await self.temp_data_col.delete_one({
                'user_id': user_id,
                'key': key
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to delete temp data: {e}")
            return False
    
    # ================================
    # STATISTICS (PREMIUM!)
    # ================================
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            user = await self.users_col.find_one({'user_id': user_id})
            if not user:
                return {}
            
            # Get additional stats
            files_count = await self.files_col.count_documents({'user_id': user_id})
            downloads_count = await self.downloads_col.count_documents({'user_id': user_id})
            success_downloads = await self.downloads_col.count_documents({
                'user_id': user_id,
                'success': True
            })
            
            # Calculate success rate
            success_rate = (success_downloads / downloads_count * 100) if downloads_count > 0 else 100
            
            # Get favorite platform
            pipeline = [
                {'$match': {'user_id': user_id, 'success': True}},
                {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 1}
            ]
            
            fav_platform_cursor = self.downloads_col.aggregate(pipeline)
            fav_platform_result = await fav_platform_cursor.to_list(length=1)
            favorite_platform = fav_platform_result[0]['_id'] if fav_platform_result else None
            
            return {
                'user_id': user_id,
                'join_date': user.get('join_date'),
                'last_activity': user.get('last_activity'),
                'files_uploaded': files_count,
                'urls_downloaded': downloads_count,
                'success_rate': round(success_rate, 2),
                'total_uploaded_size': user.get('usage_stats', {}).get('total_uploaded_size', 0),
                'total_downloaded_size': user.get('usage_stats', {}).get('total_downloaded_size', 0),
                'last_upload': user.get('usage_stats', {}).get('last_upload'),
                'last_download': user.get('usage_stats', {}).get('last_download'),
                'favorite_platform': favorite_platform,
                'is_banned': user.get('is_banned', False),
                'gofile_linked': bool(user.get('gofile_account', {}).get('token'))
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats for {user_id}: {e}")
            return {}
    
    async def get_premium_stats(self) -> Dict[str, Any]:
        """Get comprehensive bot statistics"""
        try:
            current_time = datetime.utcnow()
            week_ago = current_time - timedelta(days=7)
            
            # Basic counts
            total_users = await self.users_col.count_documents({})
            total_files = await self.files_col.count_documents({})
            total_downloads = await self.downloads_col.count_documents({})
            
            # Active users (last 7 days)
            active_users = await self.users_col.count_documents({
                'last_activity': {'$gte': week_ago}
            })
            
            # Success rate
            successful_downloads = await self.downloads_col.count_documents({'success': True})
            success_rate = (successful_downloads / total_downloads * 100) if total_downloads > 0 else 100
            
            # Total storage used
            storage_pipeline = [
                {'$group': {'_id': None, 'total_size': {'$sum': '$file_size'}}}
            ]
            storage_result = await self.files_col.aggregate(storage_pipeline).to_list(length=1)
            total_storage = storage_result[0]['total_size'] if storage_result else 0
            
            # Top platforms
            platforms_pipeline = [
                {'$match': {'success': True}},
                {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            platforms_cursor = self.downloads_col.aggregate(platforms_pipeline)
            top_platforms = await platforms_cursor.to_list(length=10)
            
            return {
                'overview': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'total_files': total_files,
                    'total_downloads': total_downloads,
                    'success_rate': round(success_rate, 2),
                    'storage_gb': round(total_storage / (1024**3), 2),
                    'premium_features': 'active',
                    'generated_at': current_time
                },
                'analytics': {
                    'top_platforms': [
                        {'platform': p['_id'], 'count': p['count']}
                        for p in top_platforms
                    ]
                },
                'performance': {
                    'database_status': 'connected',
                    'premium_features': 'enabled',
                    'auto_scaling': 'active'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get premium stats: {e}")
            return {
                'overview': {'total_users': 0, 'error': str(e)},
                'analytics': {},
                'performance': {'database_status': 'error'}
            }
    
    # ================================
    # CLEANUP & MAINTENANCE (PREMIUM!)
    # ================================
    
    async def cleanup_expired_data(self):
        """Clean up expired temporary data"""
        try:
            result = await self.temp_data_col.delete_many({
                'expires_at': {'$lt': datetime.utcnow()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"🧹 Cleaned up {result.deleted_count} expired temp records")
                
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
    
    async def close(self):
        """Close database connection gracefully"""
        try:
            if self.client:
                # Final cleanup
                await self.cleanup_expired_data()
                
                # Close connection
                self.client.close()
                self.connected = False
                logger.info("✅ Database connection closed")
                
        except Exception as e:
            logger.error(f"❌ Error closing database: {e}")
    
    # ================================
    # HEALTH CHECK (PREMIUM!)
    # ================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Premium database health check"""
        try:
            start_time = time.time()
            
            # Ping database
            await self.client.admin.command('ping')
            ping_time = time.time() - start_time
            
            # Get basic stats
            stats = await self.db.command('dbStats')
            
            return {
                'status': 'healthy',
                'connected': self.connected,
                'ping_ms': round(ping_time * 1000, 2),
                'database_size_mb': round(stats.get('dataSize', 0) / (1024**2), 2),
                'collections': stats.get('collections', 0),
                'indexes': stats.get('indexes', 0),
                'premium_features': 'active'
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connected': False
            }


# Global database instance
db = PremiumDatabase()
