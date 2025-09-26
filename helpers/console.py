import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pathlib import Path
from enum import Enum

class LogLevel(Enum):
    """Log levels với colors"""
    DEBUG = ("DEBUG", "\033[36m", "🐛")      # Cyan
    INFO = ("INFO", "\033[32m", "ℹ️")        # Green  
    WARNING = ("WARNING", "\033[33m", "⚠️")  # Yellow
    ERROR = ("ERROR", "\033[31m", "❌")      # Red
    CRITICAL = ("CRITICAL", "\033[35m", "💥") # Magenta
    SUCCESS = ("SUCCESS", "\033[92m", "✅")   # Bright Green

class ConsoleLogger:
    """Advanced console logger với colors và formatting"""
    
    def __init__(self, 
                 name: str = "Bot",
                 log_file: Optional[str] = None,
                 enable_colors: bool = True,
                 enable_file_logging: bool = True):
        self.name = name
        self.enable_colors = enable_colors and self._supports_color()
        self.enable_file_logging = enable_file_logging
        
        # Setup file logging
        if enable_file_logging:
            self._setup_file_logging(log_file)
        
        # Stats
        self.stats = {
            "debug": 0,
            "info": 0, 
            "warning": 0,
            "error": 0,
            "critical": 0,
            "success": 0
        }
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return (
            hasattr(sys.stdout, "isatty") and 
            sys.stdout.isatty() and 
            os.getenv("NO_COLOR") is None
        )
    
    def _setup_file_logging(self, log_file: Optional[str] = None) -> None:
        """Setup file logging"""
        if log_file is None:
            log_file = "logs/bot.log"
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup rotating file handler
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Get logger
        self.file_logger = logging.getLogger(f"{self.name}_file")
        self.file_logger.setLevel(logging.DEBUG)
        self.file_logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        self.file_logger.propagate = False
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_caller_info(self) -> str:
        """Get caller file and line info"""
        try:
            frame = sys._getframe(3)  # Skip log wrapper functions
            filename = os.path.basename(frame.f_code.co_filename)
            line_number = frame.f_lineno
            function_name = frame.f_code.co_name
            return f"{filename}:{function_name}:{line_number}"
        except:
            return "unknown:unknown:0"
    
    def _format_message(self, 
                       level: LogLevel, 
                       message: str,
                       extra_data: Optional[Dict[str, Any]] = None,
                       show_caller: bool = False) -> str:
        """Format log message"""
        timestamp = self._get_timestamp()
        level_name, color, emoji = level.value
        
        # Base format
        if self.enable_colors:
            formatted = f"{color}[{timestamp}] {emoji} {level_name:<8}\033[0m | {self.name} | {message}"
        else:
            formatted = f"[{timestamp}] {level_name:<8} | {self.name} | {message}"
        
        # Add caller info if requested
        if show_caller:
            caller = self._get_caller_info()
            formatted += f" | {caller}"
        
        # Add extra data
        if extra_data:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
            formatted += f" | {extra_str}"
        
        return formatted
    
    def _log(self, 
             level: LogLevel, 
             message: str,
             extra_data: Optional[Dict[str, Any]] = None,
             show_caller: bool = False,
             exc_info: bool = False) -> None:
        """Internal logging method"""
        
        # Format message
        formatted_message = self._format_message(level, message, extra_data, show_caller)
        
        # Print to console
        print(formatted_message)
        
        # Log to file
        if self.enable_file_logging:
            # Create clean message for file (no colors)
            clean_message = message
            if extra_data:
                extra_str = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
                clean_message += f" | {extra_str}"
            
            # Map custom levels to standard logging levels
            level_mapping = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
                "SUCCESS": logging.INFO  # Map SUCCESS to INFO level
            }
            
            file_level = level_mapping.get(level.value[0], logging.INFO)
            self.file_logger.log(file_level, clean_message, exc_info=exc_info)
        
        # Update stats
        self.stats[level.name.lower()] += 1
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, kwargs.get('extra'), kwargs.get('show_caller', False))
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log(LogLevel.INFO, message, kwargs.get('extra'), kwargs.get('show_caller', False))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log(LogLevel.WARNING, message, kwargs.get('extra'), kwargs.get('show_caller', True))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        exc_info = kwargs.get('exc_info', True)
        self._log(LogLevel.ERROR, message, kwargs.get('extra'), True, exc_info)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        exc_info = kwargs.get('exc_info', True)  
        self._log(LogLevel.CRITICAL, message, kwargs.get('extra'), True, exc_info)
    
    def success(self, message: str, **kwargs) -> None:
        """Log success message"""
        self._log(LogLevel.SUCCESS, message, kwargs.get('extra'), kwargs.get('show_caller', False))
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception với full traceback"""
        tb_str = traceback.format_exc()
        full_message = f"{message}\n{tb_str}"
        self._log(LogLevel.ERROR, full_message, kwargs.get('extra'), True, True)
    
    def separator(self, char: str = "=", length: int = 80) -> None:
        """Print separator line"""
        print(char * length)
    
    def banner(self, text: str, char: str = "=", padding: int = 2) -> None:
        """Print banner với text"""
        total_length = len(text) + (padding * 2)
        border = char * (total_length + 4)
        
        print(border)
        print(f"{char} {' ' * padding}{text}{' ' * padding} {char}")
        print(border)
    
    def table(self, headers: list, rows: list) -> None:
        """Print formatted table"""
        if not rows:
            return
        
        # Calculate column widths
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
        print(f"| {header_line} |")
        print(f"|{'-' * (len(header_line) + 2)}|")
        
        # Print rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print(f"| {row_line} |")
    
    def progress_bar(self, current: int, total: int, width: int = 50) -> None:
        """Print progress bar"""
        progress = current / total
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percent = progress * 100
        
        print(f"\r[{bar}] {percent:.1f}% ({current}/{total})", end="", flush=True)
        
        if current == total:
            print()  # New line when complete
    
    def get_stats(self) -> Dict[str, int]:
        """Get logging statistics"""
        return self.stats.copy()
    
    def print_stats(self) -> None:
        """Print logging statistics"""
        self.banner("Logging Statistics")
        stats_data = [
            ["Level", "Count"],
            ["DEBUG", self.stats["debug"]],
            ["INFO", self.stats["info"]],
            ["SUCCESS", self.stats["success"]],
            ["WARNING", self.stats["warning"]],
            ["ERROR", self.stats["error"]],
            ["CRITICAL", self.stats["critical"]],
        ]
        self.table(stats_data[0], stats_data[1:])

# Global logger instance
logger = ConsoleLogger()

# Convenience functions
def debug(message: str, **kwargs) -> None:
    """Log debug message"""
    logger.debug(message, **kwargs)

def info(message: str, **kwargs) -> None:
    """Log info message"""
    logger.info(message, **kwargs)

def warning(message: str, **kwargs) -> None:
    """Log warning message"""
    logger.warning(message, **kwargs)

def error(message: str, **kwargs) -> None:
    """Log error message"""
    logger.error(message, **kwargs)

def critical(message: str, **kwargs) -> None:
    """Log critical message"""
    logger.critical(message, **kwargs)

def success(message: str, **kwargs) -> None:
    """Log success message"""
    logger.success(message, **kwargs)

def exception(message: str, **kwargs) -> None:
    """Log exception với traceback"""
    logger.exception(message, **kwargs)

# Alias for backward compatibility
def add_log(message: str, level: str = "INFO", **kwargs) -> None:
    """Legacy function for backward compatibility"""
    level_map = {
        "DEBUG": debug,
        "INFO": info,
        "WARNING": warning,
        "ERROR": error,
        "CRITICAL": critical,
        "SUCCESS": success
    }
    
    log_func = level_map.get(level.upper(), info)
    log_func(message, **kwargs)

# Bot specific functions
def print_bot_info() -> None:
    """Print bot startup information"""
    from constants.bot_info import get_bot_info
    
    try:
        info_data = get_bot_info()
        logger.banner(f"🤖 {info_data['name']} Started!")
        
        startup_info = [
            ["Property", "Value"],
            ["Version", info_data['version']],
            ["Author", info_data['author']],
            ["Created", info_data['created'].strftime('%Y-%m-%d')],
            ["Support", info_data['support']],
            ["Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"],
        ]
        
        logger.table(startup_info[0], startup_info[1:])
        logger.separator()
        
    except Exception as e:
        logger.error(f"Failed to load bot info: {e}")

def print_shutdown_info() -> None:
    """Print bot shutdown information"""
    logger.banner("🛑 Bot Shutdown")
    logger.print_stats()
    logger.separator()

# Context managers
class LogContext:
    """Context manager for grouped logging"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(f"Started: {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        
        if exc_type:
            logger.error(f"Failed: {self.name} (took {duration.total_seconds():.2f}s)")
        else:
            logger.success(f"Completed: {self.name} (took {duration.total_seconds():.2f}s)")

# Usage examples
if __name__ == "__main__":
    # Test logging
    logger.debug("This is a debug message")
    logger.info("Bot is starting up", extra={"version": "1.0.0"})
    logger.success("Extension loaded successfully")
    logger.warning("This is a warning message", show_caller=True)
    logger.error("This is an error message")
    
    # Test context manager
    with LogContext("Loading extensions"):
        import time
        time.sleep(1)  # Simulate work
    
    # Test table
    logger.table(
        ["Name", "Status", "Count"],
        [
            ["Extension 1", "✅ Loaded", "5"],
            ["Extension 2", "❌ Failed", "0"],
            ["Extension 3", "✅ Loaded", "12"]
        ]
    )
    
    # Test progress bar
    for i in range(101):
        logger.progress_bar(i, 100)
        time.sleep(0.01)
    
    # Print stats
    logger.print_stats()