"""
PlexMCP Utilities Package

This package contains utility modules for the PlexMCP application, including
configuration management, logging, network operations, validation, and async utilities.
"""

# Import config utilities
from .config import (
    load_config,
    save_config,
    validate_config,
    get_config_path,
    get_config_dir,
    DEFAULT_CONFIG,
    AppConfig,
    ServerConfig,
    LoggingConfig,
    CacheConfig,
    SecurityConfig,
    FeaturesConfig
)

# Import logging utilities
from .logging_utils import (
    setup_logging,
    get_logger,
    log_execution_time,
    log_exceptions,
    LoggingContext,
    log_to_file
)

# Import network utilities
from .network import (
    is_port_open,
    async_is_port_open,
    get_local_ip,
    is_valid_ip,
    is_valid_port,
    is_plex_server_reachable,
    get_plex_auth_url,
    validate_plex_url,
    get_ssl_context
)

# Import validation utilities
from .validation import (
    ValidationError,
    validate_required,
    validate_type,
    validate_length,
    validate_regex,
    validate_enum,
    validate_range,
    validate_datetime,
    validate_uuid,
    validate_plex_token,
    validate_plex_client_identifier,
    validate_file_path,
    validate_pydantic_model,
    validate_with_schema,
    validate_condition
)

# Import async utilities
from .async_utils import (
    run_in_executor,
    run_in_process,
    AsyncLock,
    async_retry,
    TaskPool,
    create_task,
    gather_with_concurrency,
    cancel_all_tasks,
    async_timeout,
    run_until_complete_with_timeout
)
from .formatting import format_duration, format_file_size, format_date
from .network import is_plex_server_reachable, get_local_ip_address
from .async_utils import run_in_executor, async_retry
from .security import encrypt_data, decrypt_data, hash_password, verify_password

# Define __all__ to explicitly specify what gets imported with 'from utils import *'
__all__ = [
    # Config
    'load_config',
    'save_config',
    'validate_config',
    
    # Logging
    'setup_logging',
    'get_logger',
    
    # Validation
    'validate_plex_url',
    'validate_plex_token',
    
    # Formatting
    'format_duration',
    'format_file_size',
    'format_date',
    
    # Network
    'is_plex_server_reachable',
    'get_local_ip_address',
    
    # Async
    'run_in_executor',
    'async_retry',
    
    # Security
    'encrypt_data',
    'decrypt_data',
    'hash_password',
    'verify_password'
]