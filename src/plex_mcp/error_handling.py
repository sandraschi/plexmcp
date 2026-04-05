"""
Enhanced error handling for PlexMCP operations.
"""

import logging
import traceback
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PlexMCPError(Exception):
    """Base exception for PlexMCP operations."""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message)
        self.operation = operation
        self.details = details or {}


class ConnectionError(PlexMCPError):
    """Connection-related errors."""
    pass


class ValidationError(PlexMCPError):
    """Data validation errors."""
    pass


class ConfigurationError(PlexMCPError):
    """Configuration errors."""
    pass


def handle_error(
    error: Exception,
    operation: str = None,
    context: dict = None,
    logger_instance: logging.Logger = None
) -> dict[str, Any]:
    """
    Standardized error handling with proper logging and context.
    
    Returns:
        MCP-compatible error response dictionary
    """
    log = logger_instance or logger
    
    # Log full error with context
    log_context = f" | {context}" if context else ""
    log_message = f"[{operation or 'UNKNOWN'}] {type(error).__name__}: {str(error)}{log_context}"
    
    log.error(log_message, exc_info=True)
    
    # Return structured error for MCP responses
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "operation": operation,
        "context": context or {},
    }


def safe_execute(
    operation: str,
    func,
    *args,
    logger_instance: logging.Logger = None,
    **kwargs
) -> dict[str, Any]:
    """
    Safely execute a function with error handling.
    
    Returns:
        {"success": bool, "result": Any, "error": str}
    """
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "operation": operation,
        }
    except Exception as e:
        return handle_error(e, operation, kwargs, logger_instance)


def log_operation_start(operation: str, context: dict = None, logger_instance: logging.Logger = None):
    """Log the start of an operation."""
    log = logger_instance or logger
    context_str = f" | {context}" if context else ""
    log.info(f"[{operation}] START{context_str}")


def log_operation_success(operation: str, result: Any = None, context: dict = None, logger_instance: logging.Logger = None):
    """Log successful operation completion."""
    log = logger_instance or logger
    context_str = f" | {context}" if context else ""
    result_str = f" | result: {result}" if result is not None else ""
    log.info(f"[{operation}] SUCCESS{context_str}{result_str}")


def log_operation_warning(operation: str, message: str, context: dict = None, logger_instance: logging.Logger = None):
    """Log operation warning."""
    log = logger_instance or logger
    context_str = f" | {context}" if context else ""
    log.warning(f"[{operation}] WARNING: {message}{context_str}")
