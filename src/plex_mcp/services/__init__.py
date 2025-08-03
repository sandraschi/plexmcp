"""
PlexMCP Services Package

This package contains all service implementations for the PlexMCP application,
organized into logical modules for better maintainability.
"""

import logging
from typing import Dict, Any, Optional, Type, TypeVar

from .base import BaseService, ServiceError
from .plex_service import PlexService
from .playlist_service import PlaylistService
from .admin_service import AdminService

# Re-export service classes for easier importing
__all__ = [
    'ServiceError',
    'PlexService',
    'PlaylistService',
    'AdminService',
    'ServiceFactory'
]

# Type variable for service classes
T = TypeVar('T', bound=BaseService)

class ServiceFactory:
    """Factory for creating and managing service instances."""
    
    _instance = None
    _services: Dict[Type[BaseService], BaseService] = {}
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one factory exists."""
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the service factory."""
        if not self._initialized:
            self._initialized = True
            self.logger = logging.getLogger(__name__)
    
    async def get_service(self, service_class: Type[T], **kwargs) -> T:
        """Get or create a service instance.
        
        Args:
            service_class: The service class to get or create
            **kwargs: Additional arguments to pass to the service constructor
            
        Returns:
            An instance of the requested service
            
        Raises:
            ServiceError: If the service cannot be created or initialized
        """
        try:
            # Check if we already have an instance of this service
            if service_class in self._services:
                return self._services[service_class]
            
            # Create a new service instance
            self.logger.debug(f"Creating new service instance: {service_class.__name__}")
            
            # Special handling for services that depend on PlexService
            if service_class is PlexService:
                service = service_class(**kwargs)
            elif service_class in (PlaylistService, AdminService):
                # These services depend on PlexService
                plex_service = await self.get_service(PlexService, **kwargs)
                service = service_class(plex_service)
            else:
                service = service_class(**kwargs)
            
            # Initialize the service
            await service.initialize()
            
            # Store the service instance
            self._services[service_class] = service
            
            return service
            
        except Exception as e:
            error_msg = f"Failed to create service {service_class.__name__}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ServiceError(error_msg, code="service_creation_failed") from e
    
    async def close(self) -> None:
        """Close all services and clean up resources."""
        self.logger.debug("Closing all services")
        
        # Close services in reverse order of creation
        for service_class, service in reversed(list(self._services.items())):
            try:
                self.logger.debug(f"Closing service: {service_class.__name__}")
                await service.close()
            except Exception as e:
                self.logger.error(
                    f"Error closing service {service_class.__name__}: {str(e)}",
                    exc_info=True
                )
        
        # Clear the services dictionary
        self._services.clear()
    
    def __del__(self):
        """Ensure resources are cleaned up when the factory is garbage collected."""
        if self._services:
            self.logger.warning(
                "ServiceFactory was garbage collected with active services. "
                "Make sure to call close() explicitly."
            )

# Create a global service factory instance
service_factory = ServiceFactory()

# Helper function to get a service instance
async def get_service(service_class: Type[T], **kwargs) -> T:
    """Get a service instance from the global factory.
    
    Args:
        service_class: The service class to get
        **kwargs: Additional arguments to pass to the service constructor
        
    Returns:
        An instance of the requested service
    """
    return await service_factory.get_service(service_class, **kwargs)

# Helper function to close all services
async def close_services() -> None:
    """Close all services and clean up resources."""
    await service_factory.close()