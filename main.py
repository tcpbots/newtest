#!/usr/bin/env python3
"""
Premium GoFile Bot v3.0 - Main Entry Point (FIXED)
Complete rewrite with premium features and no limitations!
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_premium_logging():
    """Setup premium logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging with premium format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatters
    formatter = logging.Formatter(log_format, date_format)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        logs_dir / f"premium_bot_{today}.log",
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.FileHandler(
        logs_dir / f"errors_{today}.log",
        mode='a',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('pyrogram').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('yt_dlp').setLevel(logging.WARNING)
    
    return root_logger


def print_premium_banner():
    """Print premium bot banner"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║  🚀 PREMIUM GOFILE BOT v3.0 - COMPLETELY REBUILT! 🚀          ║
║                                                                ║
║  ✨ PREMIUM FEATURES:                                          ║
║  • 📁 Upload files up to 4GB (full Telegram support)          ║
║  • 📥 Download from 1000+ platforms (YouTube, Instagram, etc.) ║
║  • 🎥 4K video quality support                                 ║
║  • ⚡ Real-time progress tracking                              ║
║  • 🔄 Advanced retry mechanisms                                ║
║  • 📊 No artificial limits                                     ║
║  • 🛡️ Premium error handling                                   ║
║  • 🔗 GoFile account integration                               ║
║  • 📈 Advanced analytics                                       ║
║  • 🎯 Smart quality selection                                  ║
║                                                                ║
║  🔧 TECHNICAL IMPROVEMENTS:                                     ║
║  • ✅ MongoDB conflicts completely resolved                    ║
║  • ✅ yt-dlp issues fixed with premium config                  ║
║  • ✅ Progress tracking actually works                         ║
║  • ✅ Callback buttons fully functional                       ║
║  • ✅ GoFile integration perfect                               ║
║  • ✅ Premium architectures implemented                        ║
║                                                                ║
║  📚 REFERENCES:                                                ║
║  • TheHamkerCat/WilliamButcherBot (Architecture)               ║
║  • ssebastianoo/yt-dlp-telegram (Media downloading)            ║
║  • FayasNoushad/GoFile-Bot (GoFile integration)                ║
║  • nonoo/yt-dlp-telegram-bot (Premium features)                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_dependencies():
    """Check if all required dependencies are installed - FIXED VERSION"""
    logger = logging.getLogger(__name__)
    
    # Fixed: Use correct import names instead of package names
    required_imports = [
        ('pyrogram', 'pyrogram'),
        ('TgCrypto', 'TgCrypto'),
        ('motor', 'motor'),
        ('pymongo', 'pymongo'),
        ('yt_dlp', 'yt-dlp'),
        ('aiofiles', 'aiofiles'),
        ('aiohttp', 'aiohttp'),
        ('httpx', 'httpx'),
        ('orjson', 'orjson'),
        ('dotenv', 'python-dotenv'),  # Fixed: import name vs package name
        ('rich', 'rich'),
        ('tqdm', 'tqdm'),
        ('requests', 'requests')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_imports:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        logger.error("❌ Missing required packages:")
        for package in missing_packages:
            logger.error(f"   • {package}")
        logger.error("")
        logger.error("💡 Quick install:")
        logger.error(f"   pip install {' '.join(missing_packages)}")
        logger.error("")
        logger.error("💡 Or install all requirements:")
        logger.error("   pip install -r requirements-fixed.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True


def check_environment():
    """Check environment variables and configuration"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import here to avoid issues if dependencies missing
        from config_premium import Config
        config = Config()
        config.validate_config()
        logger.info("✅ Configuration is valid")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Make sure all dependencies are installed")
        return False
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("")
        logger.error("💡 Create a .env file with required values:")
        logger.error("   API_ID=your_api_id")
        logger.error("   API_HASH=your_api_hash")
        logger.error("   BOT_TOKEN=your_bot_token")
        logger.error("   ADMIN_IDS=your_user_id")
        logger.error("   MONGO_URI=mongodb://localhost:27017/")
        return False
    except Exception as e:
        logger.error(f"❌ Environment check error: {e}")
        return False


def create_example_env():
    """Create example .env file"""
    env_example = """# Premium GoFile Bot v3.0 Configuration
# Copy this to .env and fill in your values

# REQUIRED: Get from https://my.telegram.org
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# REQUIRED: Get from @BotFather  
BOT_TOKEN=your_bot_token_here

# REQUIRED: Your Telegram user ID (comma-separated for multiple admins)
ADMIN_IDS=your_user_id_here

# Database (MongoDB)
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=premium_gofile_bot

# Optional: Premium features
MAX_FILE_SIZE=4294967296
MAX_DOWNLOAD_SIZE=10737418240
MAX_CONCURRENT_UPLOADS=10
MAX_CONCURRENT_DOWNLOADS=10

# Optional: Force subscription 
FORCE_SUB_ENABLED=false
FORCE_SUB_CHANNEL=@your_channel

# Optional: GoFile API token for premium features
GOFILE_API_TOKEN=your_gofile_token

# Optional: Directory configuration
DOWNLOAD_DIR=./downloads
TEMP_DIR=./temp
COOKIES_DIR=./cookies
SESSIONS_DIR=./sessions
"""
    
    env_file = Path('.env.example')
    if not env_file.exists():
        env_file.write_text(env_example)
        return True
    return False


async def run_premium_bot():
    """Run the premium bot with advanced error handling"""
    logger = logging.getLogger(__name__)
    
    try:
        # Print premium banner
        print_premium_banner()
        
        # Setup logging
        logger.info("🚀 Starting Premium GoFile Uploader Bot v3.0...")
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Check environment
        if not check_environment():
            # Create example env file
            if create_example_env():
                logger.info("📝 Created .env.example file")
            sys.exit(1)
        
        # Import here after dependency check
        from handlers_premium import PremiumBotHandlers
        
        # Initialize premium bot
        bot = PremiumBotHandlers()
        
        # Start the bot
        logger.info("⚡ Initializing premium components...")
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("⌨️ Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


def main():
    """Main entry point"""
    
    # Setup premium logging first
    logger = setup_premium_logging()
    
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8 or higher is required")
            sys.exit(1)
        
        # Create required directories
        directories = ['downloads', 'temp', 'cookies', 'sessions', 'logs']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info(f"📁 Created required directories: {', '.join(directories)}")
        
        # Run the bot
        if sys.platform == 'win32':
            # Windows-specific event loop policy
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(run_premium_bot())
        
    except KeyboardInterrupt:
        logger.info("⌨️ Keyboard interrupt in main")
    except Exception as e:
        logger.error(f"❌ Main error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
    finally:
        logger.info("👋 Premium bot shutdown complete")


if __name__ == '__main__':
    main()
