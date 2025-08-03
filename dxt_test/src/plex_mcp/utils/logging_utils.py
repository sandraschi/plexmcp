"""
Logging utilities for PlexMCP.

This module provides functions for setting up and managing application logging.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Default log format
DEFAULT_LOG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ' [%(filename)s:%(lineno)d] [%(threadName)s]'
)

# Default date format
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format the log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logging(
    level: str = 'INFO',
    log_file: Optional[Union[str, Path]] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    max_size_mb: int = 10,
    backup_count: int = 5,
    colorize: bool = True
) -> None:
    """Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file. If None, logs to stderr.
        log_format: Log message format string.
        date_format: Date format string.
        max_size_mb: Maximum log file size in MB before rotation.
        backup_count: Number of backup log files to keep.
        colorize: Whether to use colored output in console.
    """
    # Convert level to uppercase and validate
    level = level.upper()
    if level not in LOG_LEVELS:
        level = 'INFO'
    
    # Set up formatter
    log_format = log_format or DEFAULT_LOG_FORMAT
    date_format = date_format or DEFAULT_DATE_FORMAT
    
    if colorize and not log_file:
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS[level])
    
    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_size_mb * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Use non-colored formatter for file output
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name. If None, returns the root logger.
        
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)

def log_execution_time(logger: logging.Logger = None):
    """Decorator to log the execution time of a function.
    
    Args:
        logger: Logger instance to use. If None, creates a new logger.
    """
    import time
    from functools import wraps
    
    if logger is None:
        logger = get_logger(__name__)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logger.debug(
                    f"Function {func.__name__} executed in {execution_time:.4f} seconds"
                )
        return wrapper
    return decorator

def log_exceptions(logger: logging.Logger = None, reraise: bool = True):
    """Decorator to log exceptions raised by a function.
    
    Args:
        logger: Logger instance to use. If None, creates a new logger.
        reraise: Whether to re-raise the exception after logging it.
    """
    from functools import wraps
    
    if logger is None:
        logger = get_logger(__name__)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={
                        'function': func.__name__,
                        'args': args,
                        'kwargs': kwargs
                    }
                )
                if reraise:
                    raise
        return wrapper
    return decorator

class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(
        self,
        logger: logging.Logger,
        level: Optional[int] = None,
        handler: Optional[logging.Handler] = None,
        close: bool = True
    ):
        self.logger = logger
        self.level = level
        self.handler = handler
        self.close = close
        self.old_level = None
    
    def __enter__(self):
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        
        if self.handler:
            self.logger.addHandler(self.handler)
        
        return self.logger
    
    def __exit__(self, et, ev, tb):
        if self.level is not None and self.old_level is not None:
            self.logger.setLevel(self.old_level)
        
        if self.handler:
            self.logger.removeHandler(self.handler)
        
        if self.handler and self.close:
            self.handler.close()
        
        # Don't suppress exceptions
        return False

def log_to_file(
    message: str,
    level: str = 'INFO',
    log_file: Optional[Union[str, Path]] = None,
    **kwargs
) -> None:
    """Log a message to a file with the specified level.
    
    Args:
        message: The message to log.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to the log file. If None, logs to the default logger.
        **kwargs: Additional fields to include in the log record.
    """
    level = level.upper()
    if level not in LOG_LEVELS:
        level = 'INFO'
    
    if log_file is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger('file_logger')
        if not logger.handlers:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(
                filename=log_file,
                encoding='utf-8'
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra=kwargs)
