import logging
import sys
from pathlib import Path
from typing import Optional
from app.core.config import settings

# Log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to log level
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Add module and function info for detailed logging
        if hasattr(record, 'module') and hasattr(record, 'funcName'):
            record.module_info = f"{record.module}.{record.funcName}"
        else:
            record.module_info = record.module if hasattr(record, 'module') else 'unknown'
        
        return super().format(record)

def setup_logging(
    log_level: str = "INFO",
    enable_detailed_logging: bool = False,
    log_to_file: bool = False,
    log_file_path: Optional[str] = None
) -> logging.Logger:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_detailed_logging: Enable detailed flow logging
        log_to_file: Enable file logging
        log_file_path: Path to log file (defaults to logs/app.log)
    """
    
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        if log_file_path is None:
            log_file_path = log_dir / "app.log"
    
    # Create logger
    logger = logging.getLogger("saas_api")
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    if enable_detailed_logging:
        # Detailed format with colors
        detailed_format = (
            "%(asctime)s | %(levelname)s | %(module_info)s:%(lineno)d | "
            "%(message)s"
        )
        console_formatter = ColoredFormatter(detailed_format)
    else:
        # Simple format with colors
        simple_format = "%(asctime)s | %(levelname)s | %(message)s"
        console_formatter = ColoredFormatter(simple_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # File format (no colors)
        file_format = (
            "%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | "
            "%(message)s"
        )
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance"""
    if name:
        return logging.getLogger(f"saas_api.{name}")
    return logging.getLogger("saas_api")

# Create default logger
logger = get_logger()

def log_function_call(func):
    """Decorator to log function calls and returns"""
    def wrapper(*args, **kwargs):
        logger.debug(f"🔵 CALLING: {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"🟢 RETURNING: {func.__name__} -> {result}")
            return result
        except Exception as e:
            logger.error(f"🔴 EXCEPTION in {func.__name__}: {e}")
            raise
    return wrapper

def log_database_operation(operation: str):
    """Decorator to log database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"🗄️  DB {operation.upper()}: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ DB {operation.upper()} SUCCESS: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"❌ DB {operation.upper()} FAILED: {func.__name__} - {e}")
                raise
        return wrapper
    return decorator

def log_api_request(method: str, path: str):
    """Log API request details"""
    logger.info(f"🌐 API REQUEST: {method} {path}")

def log_api_response(status_code: int, response_time: float):
    """Log API response details"""
    status_emoji = "✅" if status_code < 400 else "❌"
    logger.info(f"{status_emoji} API RESPONSE: {status_code} ({response_time:.3f}s)")

def log_authentication(user_email: str, success: bool):
    """Log authentication attempts"""
    emoji = "🔓" if success else "🔒"
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"{emoji} AUTH {status}: {user_email}")

def log_tenant_operation(operation: str, tenant_id: int, tenant_name: str):
    """Log tenant operations"""
    logger.info(f"🏢 TENANT {operation.upper()}: ID={tenant_id}, Name={tenant_name}")

def log_user_operation(operation: str, user_id: int, user_email: str, role: str):
    """Log user operations"""
    logger.info(f"👤 USER {operation.upper()}: ID={user_id}, Email={user_email}, Role={role}")

def log_token_operation(operation: str, user_email: str, token_type: str):
    """Log token operations"""
    logger.info(f"🔑 TOKEN {operation.upper()}: User={user_email}, Type={token_type}")

def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logger.error(f"💥 ERROR in {context}: {error}")

def log_warning(message: str, context: str = ""):
    """Log warnings with context"""
    logger.warning(f"⚠️  WARNING in {context}: {message}")

def log_info(message: str, context: str = ""):
    """Log info messages with context"""
    logger.info(f"ℹ️  INFO in {context}: {message}")

def log_debug(message: str, context: str = ""):
    """Log debug messages with context"""
    logger.debug(f"🔍 DEBUG in {context}: {message}") 