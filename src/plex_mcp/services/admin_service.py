"""
Admin service implementation for PlexMCP.

This module contains the AdminService class which handles administrative
operations like user management and server maintenance.
"""

import logging
import os
import time
from typing import Any

from plexapi.exceptions import Unauthorized

from ..models import ServerMaintenanceResult, UserPermissions
from .base import BaseService, ServiceError
from .rag_ingestor import HAS_RAG, get_rag_sync_progress

logger = logging.getLogger(__name__)


class AdminService(BaseService):
    """Service for administrative operations."""

    def __init__(self, plex_service):
        """Initialize the admin service.

        Args:
            plex_service: Instance of PlexService for Plex server interaction
        """
        super().__init__()
        self.plex_service = plex_service
        self.plex = None
        self.myplex_account = None

    async def _initialize(self) -> None:
        """Initialize the service."""
        await self.plex_service.initialize()
        self.plex = self.plex_service.plex

        # Try to get MyPlex account if available
        try:
            if hasattr(self.plex, "myPlexAccount"):
                self.myplex_account = self.plex.myPlexAccount()
        except Exception as e:
            logger.warning(f"Failed to get MyPlex account: {str(e)}")

    async def get_users(self) -> list[UserPermissions]:
        """Get all users with access to the Plex server.

        Returns:
            List of user accounts and their permissions
        """
        await self.initialize()

        try:
            users = []

            # Get server owner (admin) first
            if self.myplex_account and self.myplex_account.email:
                users.append(self._create_admin_user_permissions(self.myplex_account))

            # Get managed users (home users)
            if hasattr(self.plex, "myPlexAccount") and hasattr(self.plex.myPlexAccount(), "users"):
                for user in self.plex.myPlexAccount().users():
                    users.append(self._convert_to_user_permissions(user))

            # Get local users (if any)
            # Note: This requires Plex Pass and the server to be claimed
            if hasattr(self.plex, "myPlexUsers"):
                for user in self.plex.myPlexUsers():
                    if not any(u.user_id == str(user.id) for u in users):
                        users.append(self._convert_to_user_permissions(user))

            return users

        except Unauthorized as e:
            error_msg = "Unauthorized: Admin privileges required to access user information"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="unauthorized") from e
        except Exception as e:
            error_msg = f"Failed to get users: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="get_users_failed") from e

    async def update_user_permissions(self, user_id: str, permissions: dict[str, Any]) -> UserPermissions:
        """Update user permissions and restrictions.

        Args:
            user_id: ID of the user to update
            permissions: Dictionary of permissions to update

        Returns:
            Updated user permissions
        """
        await self.initialize()

        try:
            # This is a simplified example - actual implementation would use Plex API
            # to update user permissions on the server

            # In a real implementation, we would:
            # 1. Find the user by ID
            # 2. Update their permissions using the Plex API
            # 3. Return the updated user object

            # For now, we'll just log the update and return a mock response
            logger.info(f"Updating permissions for user {user_id}: {permissions}")

            # Simulate a successful update
            return UserPermissions(
                user_id=user_id,
                username=permissions.get("username", f"user_{user_id}"),
                email=permissions.get("email", f"user_{user_id}@example.com"),
                is_admin=permissions.get("is_admin", False),
                is_managed=permissions.get("is_managed", True),
                library_access=permissions.get("library_access", []),
                restricted_content=permissions.get("restricted_content", False),
                max_rating=permissions.get("max_rating"),
                sharing_enabled=permissions.get("sharing_enabled", False),
                sync_enabled=permissions.get("sync_enabled", False),
                home_user=permissions.get("home_user", False),
                last_seen=int(time.time()),
                restrictions=permissions.get("restrictions", []),
            )

        except Exception as e:
            error_msg = f"Failed to update user permissions: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="update_user_failed") from e

    async def run_server_maintenance(
        self, operation: str, options: dict[str, Any] | None = None
    ) -> ServerMaintenanceResult:
        """Run server maintenance operations.

        Args:
            operation: Type of maintenance to perform
                      (optimize, clean_bundles, empty_trash, etc.)
            options: Additional options for the operation

        Returns:
            Result of the maintenance operation
        """
        await self.initialize()

        try:
            logger.info(f"Triggering maintenance operation: {operation}")
            start_time = time.time()

            # Execute real operations via PlexAPI
            if operation == "optimize":
                await self.plex_service._run_in_executor(self.plex.library.optimize)
            elif operation == "clean_bundles":
                await self.plex_service._run_in_executor(self.plex.library.cleanBundles)
            elif operation == "empty_trash":
                # Empty trash for all sections
                for section in self.plex.library.sections():
                    await self.plex_service._run_in_executor(section.emptyTrash)
            else:
                logger.warning(f"Maintenance operation '{operation}' not explicitly supported, trying library update.")
                await self.plex_service._run_in_executor(self.plex.library.update)

            duration = time.time() - start_time

            result_details = {
                "operation": operation,
                "options": options or {},
                "completed_at": int(time.time()),
                "status": "completed",
                "duration_seconds": round(duration, 2),
            }

            return ServerMaintenanceResult(
                operation=operation,
                status="success",
                details=result_details,
                space_freed_gb=0.0,  # Plex API doesn't return space freed directly
                items_processed=0,
                duration_seconds=duration,
                recommendations=[
                    "Maintain a regular schedule for library optimization to ensure peak performance.",
                ],
                next_recommended=int(time.time()) + (7 * 24 * 3600),
                warnings=[],
            )

        except Exception as e:
            error_msg = f"Failed to run maintenance operation {operation}: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="maintenance_failed") from e

    async def get_server_health(self) -> dict[str, Any]:
        """Get detailed server health and performance metrics.

        Returns:
            Dictionary containing server health information
        """
        await self.initialize()

        try:
            # Get basic server status
            server_status = await self.plex_service.get_server_status()

            # Get active sessions
            sessions = await self.plex_service._run_in_executor(self.plex.sessions)
            transcode_sessions = getattr(self.plex, "transcodeSessions", lambda: [])
            if callable(transcode_sessions):
                transcode_sessions = await self.plex_service._run_in_executor(transcode_sessions)

            # Check for any active alerts
            alerts = []

            # Surface version as health data
            return {
                "status": "healthy",
                "timestamp": int(time.time()),
                "server": {
                    "name": server_status.name,
                    "version": server_status.version,
                    "platform": server_status.platform,
                    "my_plex_connected": server_status.connected,
                },
                "load": {
                    "active_sessions": len(sessions),
                    "transcode_sessions": len(transcode_sessions),
                },
                "background_tasks": {
                    "running": 0,  # Plex API doesn't expose task counts easily
                    "status": "operational",
                },
                "rag": self._get_rag_stats(),
                "alerts": alerts,
            }

        except Exception as e:
            error_msg = f"Failed to get server health: {str(e)}"
            logger.error(error_msg)
            raise ServiceError(error_msg, code="health_check_failed") from e

    def _get_rag_stats(self) -> dict[str, Any]:
        """Get RAG indexing and storage statistics."""
        if not HAS_RAG:
            return {"available": False}

        try:
            from .rag_ingestor import PlexIngestor

            ingestor = PlexIngestor(self.plex_service)
            db_path = ingestor.db_path

            # Calculate directory size
            total_size_mb = 0.0
            item_count = 0
            if os.path.exists(db_path):
                for dirpath, _, filenames in os.walk(db_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_size_mb += os.path.getsize(fp) / (1024 * 1024)

                # Try to get item count from progress if idle, or assume 0 if first run
                progress = get_rag_sync_progress()
                item_count = progress.get("indexed_count", 0)

            return {
                "available": True,
                "backend": "lancedb",
                "storage_mb": round(total_size_mb, 2),
                "item_count": item_count,
                "db_path": db_path,
                "sync_status": get_rag_sync_progress().get("phase", "idle"),
            }
        except Exception as e:
            logger.error(f"Error gathering RAG stats: {e}")
            return {"available": True, "error": str(e)}

    # Helper methods
    def _create_admin_user_permissions(self, account) -> UserPermissions:
        """Create a UserPermissions object for the admin user."""
        return UserPermissions(
            user_id=account.id,
            username=account.username,
            email=account.email,
            is_admin=True,
            is_managed=False,
            library_access=[],  # Admin has access to all libraries
            restricted_content=False,
            max_rating=None,
            sharing_enabled=True,
            sync_enabled=True,
            home_user=True,
            last_seen=int(time.time()),
            restrictions=[],
        )

    def _convert_to_user_permissions(self, user) -> UserPermissions:
        """Convert a Plex user object to our UserPermissions model."""
        return UserPermissions(
            user_id=user.id,
            username=user.username or user.title or f"user_{user.id}",
            email=getattr(user, "email", ""),
            is_admin=getattr(user, "admin", False),
            is_managed=getattr(user, "restricted", False),
            library_access=getattr(user, "sections", []),
            restricted_content=getattr(user, "restricted", False),
            max_rating=getattr(user, "rating", None),
            sharing_enabled=getattr(user, "sharing", False),
            sync_enabled=getattr(user, "sync", False),
            home_user=getattr(user, "home", False),
            last_seen=getattr(user, "lastSeenAt", 0),
            restrictions=getattr(user, "restrictions", []),
        )
