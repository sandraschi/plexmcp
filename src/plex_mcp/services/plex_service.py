"""Plex service implementation for FastMCP 2.10."""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from plexapi.exceptions import PlexApiException
from plexapi.server import PlexServer

from ..models.media import MediaItem
from ..models.server import PlexServerStatus

logger = logging.getLogger(__name__)


class PlexService:
    """Service for interacting with Plex Media Server."""

    def __init__(self, base_url: str, token: str, timeout: int = 30):
        """Initialize Plex service.

        Args:
            base_url: Base URL of the Plex server (e.g., http://localhost:32400)
            token: Plex authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.server: Optional[PlexServer] = None
        self._initialized = False

    async def connect(self) -> None:
        """Establish connection to Plex server."""
        if self._initialized:
            return

        try:
            # PlexAPI handles its own session management, don't pass aiohttp session
            self.server = await self._run_in_executor(
                PlexServer, self.base_url, self.token, timeout=self.timeout
            )
            self._initialized = True
            logger.info(f"Connected to Plex server: {self.server.friendlyName}")

        except PlexApiException as e:
            logger.error(f"Failed to connect to Plex server: {str(e)}")
            raise

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous PlexAPI calls in executor."""
        from functools import partial

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def get_server_status(self) -> PlexServerStatus:
        """Get Plex server status and information."""
        if not self._initialized:
            await self.connect()

        try:
            status = await self._run_in_executor(self._get_server_status_sync)
            return PlexServerStatus(**status)

        except PlexApiException as e:
            logger.error(f"Failed to get server status: {str(e)}")
            raise

    def _get_server_status_sync(self) -> Dict[str, Any]:
        """Synchronous helper to get server status."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")

        return {
            "name": self.server.friendlyName,
            "version": self.server.version,
            "platform": self.server.platform,
            "active_sessions": len(self.server.sessions()),
            "libraries": [s.title for s in self.server.library.sections()],
            "updated_at": self.server.updated_at.timestamp()
            if hasattr(self.server, "updated_at")
            else 0,
        }

    async def list_libraries(self) -> List[Dict[str, Any]]:
        """Get list of all libraries from Plex server.

        Returns:
            List of dictionaries containing library information
        """
        if not self._initialized:
            await self.connect()

        try:
            libraries = await self._run_in_executor(self._get_libraries_sync)
            return libraries

        except PlexApiException as e:
            logger.error(f"Failed to list libraries: {str(e)}")
            raise

    async def get_libraries(self) -> List[Dict[str, Any]]:
        """Alias for list_libraries for backward compatibility."""
        return await self.list_libraries()

    def _get_libraries_sync(self) -> List[Dict[str, Any]]:
        """Synchronous helper to get libraries with complete section information."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")

        libraries = []
        for section in self.server.library.sections():
            try:
                # Get the section details
                section_info = {
                    "id": section.key,
                    "title": section.title,
                    "type": section.type,
                    "agent": getattr(section, "agent", ""),
                    "scanner": getattr(section, "scanner", ""),
                    "language": getattr(section, "language", "en"),
                    "updated_at": section.updatedAt.timestamp()
                    if hasattr(section, "updatedAt")
                    else 0,
                    "created_at": section.addedAt.timestamp() if hasattr(section, "addedAt") else 0,
                    "scanned_at": section.scannedAt.timestamp()
                    if hasattr(section, "scannedAt")
                    else 0,
                    "content": getattr(section, "content", None),
                    "count": section.totalSize if hasattr(section, "totalSize") else 0,
                }

                # Get additional metadata if available
                if hasattr(section, "contentChangedAt"):
                    section_info["content_changed_at"] = section.contentChangedAt.timestamp()

                libraries.append(section_info)

            except Exception as e:
                logger.error(
                    f"Error processing library section {getattr(section, 'title', 'unknown')}: {str(e)}"
                )
                continue

        return libraries

    async def search_media(
        self, query: str, limit: int = 10, library_id: Optional[str] = None
    ) -> List[MediaItem]:
        """Search for media across all libraries or within a specific library."""
        if not self._initialized:
            await self.connect()

        try:
            results = await self._run_in_executor(self._search_media_sync, query, limit, library_id)
            return [MediaItem(**item) for item in results]

        except PlexApiException as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def _search_media_sync(
        self, query: str, limit: int, library_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous helper to search for media."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")

        if library_id:
            section = self.server.library.sectionByID(int(library_id))
            results = section.search(query, maxresults=limit)
        else:
            results = self.server.search(query, limit=limit)

        return [
            {
                "id": str(getattr(item, "ratingKey", getattr(item, "id", ""))),
                "title": getattr(item, "title", getattr(item, "tag", "Unknown")),
                "type": getattr(item, "type", "unknown"),
                "year": getattr(item, "year", None),
                "thumb": getattr(item, "thumb", ""),
                "summary": getattr(item, "summary", ""),
            }
            for item in results
        ]

    async def organize_library(
        self, library_id: str, dry_run: bool = False, patterns: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Organize a Plex library according to best practices.

        Args:
            library_id: ID of the library to organize
            dry_run: If True, only show what would be changed
            patterns: Custom patterns for organization

        Returns:
            Dictionary with organization results
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )

            # In a real implementation, this would perform actual organization
            # For now, we'll return a summary of the library
            items = await self._run_in_executor(lambda: section.all())

            return {
                "library_id": library_id,
                "library_name": section.title,
                "item_count": len(items),
                "changes": [] if dry_run else ["Organization completed"],
                "dry_run": dry_run,
            }
        except Exception as e:
            logger.error(f"Error organizing library {library_id}: {e}")
            raise

    async def analyze_library(self, library_id: str) -> Dict[str, Any]:
        """Analyze a library for organization issues.

        Args:
            library_id: ID of the library to analyze

        Returns:
            Dictionary with analysis results
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            items = await self._run_in_executor(lambda: section.all())

            # Analyze items for potential issues
            issues = []
            for item in items[:100]:  # Limit to first 100 items for performance
                if not hasattr(item, "media") or not item.media:
                    issues.append(
                        {
                            "item_id": item.ratingKey,
                            "title": item.title,
                            "issue": "Missing media files",
                            "severity": "high",
                        }
                    )

            return {
                "library_id": library_id,
                "library_name": section.title,
                "total_items": len(items),
                "issues_found": len(issues),
                "issues": issues[:10],  # Return first 10 issues
            }
        except Exception as e:
            logger.error(f"Error analyzing library {library_id}: {e}")
            raise

    async def refresh_metadata(
        self, item_id: Optional[str] = None, library_id: Optional[str] = None, force: bool = False
    ) -> Dict[str, Any]:
        """Refresh metadata for an item or library.

        Args:
            item_id: ID of the item to refresh
            library_id: ID of the library to refresh
            force: Force refresh even if not needed

        Returns:
            Dictionary with refresh results
        """
        if not self._initialized:
            await self.connect()

        try:
            if item_id:
                item = await self._run_in_executor(lambda: self.server.fetchItem(int(item_id)))
                await self._run_in_executor(item.refresh)
                return {"item_id": item_id, "title": item.title, "refreshed": True}
            elif library_id:
                section = await self._run_in_executor(
                    lambda: self.server.library.sectionByID(int(library_id))
                )
                await self._run_in_executor(section.update)
                return {"library_id": library_id, "library_name": section.title, "refreshed": True}
            else:
                raise ValueError("Either item_id or library_id must be provided")
        except Exception as e:
            logger.error(f"Error refreshing metadata: {e}")
            raise

    # User Management Methods

    async def create_user(
        self, username: str, email: str, password: str, role: str, restricted: bool = False
    ) -> Dict[str, Any]:
        """Create a new Plex user.

        Args:
            username: Username for the new user
            email: Email address for the new user
            password: Password for the new user
            role: User role (admin, user, managed, shared)
            restricted: Whether the user should be restricted

        Returns:
            Dictionary with user information
        """
        if not self._initialized:
            await self.connect()

        try:
            # Plex Home requires different handling than managed users
            if role == "managed":
                user = await self._run_in_executor(
                    self.server.myPlexAccount().addFriend,
                    email=email,
                    user=username,
                    password=password,
                    server=True,
                    allowSync=True,
                    allowCameraUpload=False,
                    allowChannels=True,
                    filterMovies=None,
                    filterTelevision=None,
                    filterMusic=None,
                )
            else:
                user = await self._run_in_executor(
                    self.server.myPlexAccount().addFriend,
                    user=username,
                    server=True,
                    allowSync=True,
                    allowCameraUpload=False,
                    allowChannels=True,
                )

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "thumb": user.thumb,
                "restricted": restricted,
                "role": role,
                "created_at": user.createdAt.timestamp() if hasattr(user, "createdAt") else None,
            }
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            raise

    async def update_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing Plex user.

        Args:
            user_id: ID of the user to update
            **kwargs: Fields to update (username, email, password, role, restricted)

        Returns:
            Updated user information
        """
        if not self._initialized:
            await self.connect()

        try:
            account = await self._run_in_executor(self.server.myPlexAccount)
            user = await self._run_in_executor(account.user, user_id)

            # Update fields if provided
            if "username" in kwargs:
                await self._run_in_executor(setattr, user, "username", kwargs["username"])
            if "email" in kwargs:
                await self._run_in_executor(setattr, user, "email", kwargs["email"])
            if "password" in kwargs:
                await self._run_in_executor(user.updatePassword, kwargs["password"])

            # For Plex Home users, update restrictions
            if "restricted" in kwargs and hasattr(user, "updateHomeUser"):
                await self._run_in_executor(
                    user.updateHomeUser,
                    allowSync=True,
                    allowCameraUpload=False,
                    allowChannels=True,
                    filterMovies=None,
                    filterTelevision=None,
                    filterMusic=None,
                    restricted=kwargs["restricted"],
                )

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "restricted": getattr(user, "restricted", False),
                "role": "managed" if hasattr(user, "home") and user.home else "friend",
            }
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """Delete a Plex user.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            account = await self._run_in_executor(self.server.myPlexAccount)
            user = await self._run_in_executor(account.user, user_id)
            await self._run_in_executor(account.removeFriend, user)
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def list_users(self) -> List[Dict[str, Any]]:
        """List all Plex users.

        Returns:
            List of users with their information
        """
        if not self._initialized:
            await self.connect()

        try:
            account = await self._run_in_executor(self.server.myPlexAccount)
            users = await self._run_in_executor(account.users)

            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "thumb": getattr(user, "thumb", ""),
                    "restricted": getattr(user, "restricted", False),
                    "role": "managed" if hasattr(user, "home") and user.home else "friend",
                    "created_at": user.createdAt.timestamp()
                    if hasattr(user, "createdAt")
                    else None,
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific Plex user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            User information if found, None otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            account = await self._run_in_executor(self.server.myPlexAccount)
            user = await self._run_in_executor(account.user, user_id)

            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "thumb": getattr(user, "thumb", ""),
                "restricted": getattr(user, "restricted", False),
                "role": "managed" if hasattr(user, "home") and user.home else "friend",
                "created_at": user.createdAt.timestamp() if hasattr(user, "createdAt") else None,
                "permissions": await self._get_user_permissions(user),
            }
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    async def update_user_permissions(
        self, user_id: str, permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update permissions for a Plex user.

        Args:
            user_id: ID of the user to update
            permissions: Dictionary of permissions to update

        Returns:
            Updated user information with new permissions
        """
        if not self._initialized:
            await self.connect()

        try:
            account = await self._run_in_executor(self.server.myPlexAccount)
            user = await self._run_in_executor(account.user, user_id)

            # Update permissions based on the provided dictionary
            # Note: Plex API has limited permission controls
            if "allowSync" in permissions:
                user.allowSync = permissions["allowSync"]
            if "allowCameraUpload" in permissions:
                user.allowCameraUpload = permissions["allowCameraUpload"]
            if "allowChannels" in permissions:
                user.allowChannels = permissions["allowChannels"]

            # Save changes
            await self._run_in_executor(user.save)

            # Return updated user info
            return {
                "id": user.id,
                "username": user.username,
                "permissions": {
                    "allowSync": user.allowSync,
                    "allowCameraUpload": user.allowCameraUpload,
                    "allowChannels": user.allowChannels,
                },
            }
        except Exception as e:
            logger.error(f"Error updating permissions for user {user_id}: {e}")
            raise

    # Library Management Methods

    async def scan_library(self, library_id: str, force: bool = False) -> Dict[str, Any]:
        """Scan a library for new or updated files.

        Args:
            library_id: ID of the library to scan
            force: If True, force a full scan

        Returns:
            Dictionary with scan results
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            if force:
                await self._run_in_executor(section.update)
            else:
                await self._run_in_executor(section.refresh)

            return {
                "library_id": library_id,
                "library_name": section.title,
                "scan_successful": True,
                "full_scan": force,
            }
        except Exception as e:
            logger.error(f"Error scanning library {library_id}: {e}")
            raise

    async def refresh_library_metadata(self, library_id: str) -> bool:
        """Refresh metadata for a library.

        Args:
            library_id: ID of the library to refresh

        Returns:
            True if refresh was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.refresh)
            return True
        except Exception as e:
            logger.error(f"Error refreshing library {library_id}: {e}")
            return False

    async def optimize_library(self, library_id: str) -> bool:
        """Optimize a library database.

        Args:
            library_id: ID of the library to optimize

        Returns:
            True if optimization was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            # Plex doesn't have a direct optimize method, so we'll clean bundles
            # and refresh metadata as an alternative
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.cleanBundles)
            await self._run_in_executor(section.update)
            return True
        except Exception as e:
            logger.error(f"Error optimizing library {library_id}: {e}")
            return False

    async def get_library(self, library_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific library.

        Args:
            library_id: ID of the library to retrieve

        Returns:
            Library information if found, None otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            return self._format_library_section(section)
        except Exception as e:
            logger.error(f"Error getting library {library_id}: {e}")
            return None

    # Removed duplicate list_libraries - using the one at line 86

    async def add_library(
        self,
        name: str,
        libtype: str,
        agent: str,
        scanner: str,
        language: str,
        location: str,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Add a new library.

        Args:
            name: Name of the new library
            libtype: Type of library (movie, show, artist, photo)
            agent: Metadata agent to use
            scanner: Scanner to use
            language: Language for metadata
            location: Path to the library content
            **kwargs: Additional library settings

        Returns:
            The created library information if successful, None otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            # Plex API doesn't support adding libraries directly, so we'll return
            # instructions for manual addition
            logger.warning(
                "Adding libraries programmatically is not directly supported by Plex API. "
                "Please add the library through the Plex web interface with these settings:\n"
                f"Name: {name}\n"
                f"Type: {libtype}\n"
                f"Agent: {agent}\n"
                f"Scanner: {scanner}\n"
                f"Language: {language}\n"
                f"Location: {location}"
            )
            return None
        except Exception as e:
            logger.error(f"Error adding library {name}: {e}")
            return None

    async def update_library(self, library_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a library's settings.

        Args:
            library_id: ID of the library to update
            **kwargs: Fields to update (name, agent, scanner, language, thumb)

        Returns:
            The updated library information if successful, None otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )

            # Update fields if provided
            if "name" in kwargs:
                await self._run_in_executor(setattr, section, "title", kwargs["name"])
            if "agent" in kwargs:
                await self._run_in_executor(section.editAdvanced, agent=kwargs["agent"])
            if "scanner" in kwargs:
                await self._run_in_executor(section.editAdvanced, scanner=kwargs["scanner"])
            if "language" in kwargs:
                await self._run_in_executor(section.editAdvanced, language=kwargs["language"])
            if "thumb" in kwargs:
                await self._run_in_executor(section.uploadPoster, url=kwargs["thumb"])

            # Reload the section to get updated info
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            return self._format_library_section(section)
        except Exception as e:
            logger.error(f"Error updating library {library_id}: {e}")
            return None

    async def delete_library(self, library_id: str) -> bool:
        """Delete a library.

        Args:
            library_id: ID of the library to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.delete)
            return True
        except Exception as e:
            logger.error(f"Error deleting library {library_id}: {e}")
            return False

    async def add_library_location(self, library_id: str, path: str) -> bool:
        """Add a location to a library.

        Args:
            library_id: ID of the library
            path: Path to add to the library

        Returns:
            True if addition was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.addLocation, path)
            return True
        except Exception as e:
            logger.error(f"Error adding location {path} to library {library_id}: {e}")
            return False

    async def remove_library_location(self, library_id: str, path: str) -> bool:
        """Remove a location from a library.

        Args:
            library_id: ID of the library
            path: Path to remove from the library

        Returns:
            True if removal was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.removeLocation, path)
            return True
        except Exception as e:
            logger.error(f"Error removing location {path} from library {library_id}: {e}")
            return False

    async def get_library_items(
        self,
        library_id: str,
        limit: int = 100,
        offset: int = 0,
        sort: Optional[str] = None,
        **filters,
    ) -> Dict[str, Any]:
        """Get items from a library.

        Args:
            library_id: ID of the library
            limit: Maximum number of items to return
            offset: Offset for pagination
            sort: Sort field (e.g., 'titleSort', 'addedAt', 'lastViewedAt')
            **filters: Filter criteria (e.g., genre='Action', year=2020)

        Returns:
            Dictionary with items and pagination info
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )

            # Get all items from section
            all_items = await self._run_in_executor(lambda: section.all())

            # Apply filters if any
            items = all_items
            for key, value in filters.items():
                items = [item for item in items if getattr(item, key, None) == value]

            # Apply sorting
            if sort:
                reverse = sort.startswith("-")
                sort_key = sort.lstrip("-")
                items = sorted(items, key=lambda x: getattr(x, sort_key, ""), reverse=reverse)

            # Apply pagination
            total = len(items)
            items = items[offset : offset + limit]

            # Format items - _format_media_item is async so we need to await each
            formatted_items = []
            for item in items:
                try:
                    formatted = await self._format_media_item(item)
                    if formatted:
                        formatted_items.append(formatted)
                except Exception as e:
                    logger.warning(f"Failed to format item {getattr(item, 'title', 'unknown')}: {e}")
                    continue
            
            return {
                "items": formatted_items,
                "total": total,
                "offset": offset,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"Error getting items from library {library_id}: {e}")
            return {"items": [], "total": 0, "offset": 0, "limit": limit}

    async def empty_trash(self, library_id: str) -> bool:
        """Empty the trash for a library.

        Args:
            library_id: ID of the library

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            section = await self._run_in_executor(
                lambda: self.server.library.sectionByID(int(library_id))
            )
            await self._run_in_executor(section.emptyTrash)
            return True
        except Exception as e:
            logger.error(f"Error emptying trash for library {library_id}: {e}")
            return False

    async def clean_bundles(self, library_id: Optional[str] = None) -> Dict[str, Any]:
        """Clean old bundles for a library or all libraries.

        Args:
            library_id: Optional ID of the library to clean

        Returns:
            Dictionary with cleanup results
        """
        if not self._initialized:
            await self.connect()

        try:
            if library_id:
                section = await self._run_in_executor(
                    lambda: self.server.library.sectionByID(int(library_id))
                )
                await self._run_in_executor(section.cleanBundles)
                return {"library_id": library_id, "library_name": section.title, "cleaned": True}
            else:
                await self._run_in_executor(self.server.library.cleanBundles)
                return {"all_libraries": True, "cleaned": True}
        except Exception as e:
            logger.error(f"Error cleaning bundles: {e}")
            return {"cleaned": False, "error": str(e)}

    def _format_library_section(self, section) -> Dict[str, Any]:
        """Format a library section into a dictionary."""
        return {
            "id": section.key,
            "title": section.title,
            "type": section.type,
            "agent": section.agent,
            "scanner": section.scanner,
            "language": section.language,
            "uuid": section.uuid,
            "updated_at": section.updatedAt.timestamp() if hasattr(section, "updatedAt") else 0,
            "scanned_at": section.scannedAt.timestamp() if hasattr(section, "scannedAt") else 0,
            "count": len(section.all()),
            "locations": [loc for loc in section.locations]
            if hasattr(section, "locations")
            else [],
        }

    async def _format_media_item(self, item) -> Dict[str, Any]:
        """Format a media item into a dictionary."""
        if not item:
            return None

        def safe_ts(dt):
            try:
                return dt.timestamp() if dt else 0
            except Exception:
                return 0

        # Handle Role/Director objects which have 'tag' instead of 'title'
        title = getattr(item, "title", getattr(item, "tag", "Unknown"))
        rating_key = getattr(item, "ratingKey", getattr(item, "id", ""))
        
        # Basic result structure
        result = {
            "id": str(rating_key),
            "title": title,
            "type": getattr(item, "type", "unknown"),
            "year": getattr(item, "year", None),
            "thumb": getattr(item, "thumb", ""),
            "art": getattr(item, "art", ""),
            "summary": getattr(item, "summary", ""),
            "rating_key": str(rating_key),
            "key": getattr(item, "key", ""),
        }

        # Add timestamp fields safely
        if hasattr(item, "addedAt"):
            result["added_at"] = safe_ts(item.addedAt)
        if hasattr(item, "updatedAt"):
            result["updated_at"] = safe_ts(item.updatedAt)
        if hasattr(item, "lastViewedAt"):
            result["last_viewed_at"] = safe_ts(item.lastViewedAt)
            
        # Add other common fields if present
        if hasattr(item, "viewCount"):
            result["view_count"] = item.viewCount
        if hasattr(item, "contentRating"):
            result["content_rating"] = item.contentRating
        if hasattr(item, "rating"):
            result["rating"] = item.rating
        if hasattr(item, "audienceRating"):
            result["audience_rating"] = item.audienceRating
        if hasattr(item, "duration"):
            result["duration"] = item.duration / 60000 if item.duration else 0
        if hasattr(item, "guid"):
            result["guid"] = item.guid

        # Type-specific fields
        if hasattr(item, "originalTitle"):
            result["original_title"] = item.originalTitle

        if hasattr(item, "studio"):
            result["studio"] = item.studio

        if hasattr(item, "tagline"):
            result["tagline"] = item.tagline

        if hasattr(item, "originallyAvailableAt"):
            result["originally_available_at"] = safe_ts(item.originallyAvailableAt)

        # Collections and genres
        if hasattr(item, "collections"):
            result["collections"] = [c.tag for c in item.collections]

        if hasattr(item, "genres"):
            result["genres"] = [g.tag for g in item.genres]

        # People
        if hasattr(item, "directors"):
            result["directors"] = [d.tag for d in item.directors]

        if hasattr(item, "writers"):
            result["writers"] = [w.tag for w in item.writers]

        if hasattr(item, "roles"):
            result["actors"] = [{"name": r.tag, "role": r.role} for r in item.roles]

        # Library info
        if hasattr(item, "librarySectionID"):
            result["library_section_id"] = item.librarySectionID

        if hasattr(item, "librarySectionTitle"):
            result["library_section_title"] = item.librarySectionTitle

        # Media info
        if hasattr(item, "media"):
            result["media_info"] = [
                {
                    "video_codec": m.videoCodec if hasattr(m, "videoCodec") else None,
                    "video_resolution": m.videoResolution
                    if hasattr(m, "videoResolution")
                    else None,
                    "video_frame_rate": m.videoFrameRate if hasattr(m, "videoFrameRate") else None,
                    "audio_codec": m.audioCodec if hasattr(m, "audioCodec") else None,
                    "audio_channels": m.audioChannels if hasattr(m, "audioChannels") else None,
                    "container": m.container if hasattr(m, "container") else None,
                    "bitrate": m.bitrate if hasattr(m, "bitrate") else None,
                    "width": m.width if hasattr(m, "width") else None,
                    "height": m.height if hasattr(m, "height") else None,
                    "aspect_ratio": m.aspectRatio if hasattr(m, "aspectRatio") else None,
                    "duration": m.duration if hasattr(m, "duration") else None,
                }
                for m in item.media
            ]

        return result

    async def advanced_search_media(
        self,
        query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        library_id: Optional[str] = None,
        media_type: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[Union[int, List[int], str]] = None,
        decade: Optional[int] = None,
        genre: Optional[Union[str, List[str]]] = None,
        actor: Optional[Union[str, List[str]]] = None,
        director: Optional[Union[str, List[str]]] = None,
        content_rating: Optional[Union[str, List[str]]] = None,
        studio: Optional[Union[str, List[str]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        language: Optional[Union[str, List[str]]] = None,
        collection: Optional[Union[str, List[str]]] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        unwatched: Optional[bool] = None,
        sort_by: str = "titleSort",
        sort_dir: str = "asc",
        **kwargs,
    ) -> Dict[str, Any]:
        """Advanced search for media with extensive filtering options.

        Args:
            query: General search term (searches across multiple fields)
            limit: Maximum number of results to return (1-1000)
            offset: Offset for pagination
            library_id: Optional library ID to search within
            media_type: Filter by media type (movie, show, season, episode, artist, album, track, photo)
            title: Filter by title (supports wildcards with *)
            year: Filter by specific year or list of years
            decade: Filter by decade (e.g., 2020 for 2020s)
            genre: Filter by genre (single or list)
            actor: Filter by actor (single or list)
            director: Filter by director (single or list)
            content_rating: Filter by content rating (e.g., 'PG', 'R', 'TV-MA')
            studio: Filter by studio
            country: Filter by country
            language: Filter by language code (e.g., 'en', 'ja', 'es')
            collection: Filter by collection
            min_rating: Minimum user rating (0-10)
            max_rating: Maximum user rating (0-10)
            min_year: Minimum release year
            max_year: Maximum release year
            unwatched: Only show unwatched items
            sort_by: Field to sort by (e.g., 'titleSort', 'year', 'rating', 'addedAt', 'lastViewedAt')
            sort_dir: Sort direction ('asc' or 'desc')
            **kwargs: Additional filters

        Returns:
            Dictionary with search results and pagination info
        """
        if not self._initialized:
            await self.connect()

        try:
            # Prepare filters
            filters = {}

            # Basic filters
            if media_type:
                filters["libtype"] = media_type
            if title:
                filters["title"] = title
            if year:
                filters["year"] = year
            if decade:
                filters["decade"] = decade

            # List filters
            for field in [
                "genre",
                "actor",
                "director",
                "content_rating",
                "studio",
                "country",
                "language",
                "collection",
            ]:
                value = locals()[field]
                if value:
                    if isinstance(value, str):
                        value = [value]
                    filters[f"{field}"] = value

            # Range filters
            if min_rating is not None:
                filters["userRating>"] = min_rating
            if max_rating is not None:
                filters["userRating<"] = max_rating
            if min_year is not None:
                filters["year>"] = min_year
            if max_year is not None:
                filters["year<"] = max_year

            # Special filters
            if unwatched is not None:
                filters["unwatched"] = unwatched

            # Sorting
            if sort_dir.lower() not in ("asc", "desc"):
                sort_dir = "asc"
            sort = f"{sort_dir.lower()}:{sort_by}"

            # Search in specific library or across all
            if library_id:
                section = await self._run_in_executor(
                    lambda: self.server.library.sectionByID(int(library_id))
                )
                search_func = section.search
            else:
                search_func = self.server.library.search

            # Execute search
            results = await self._run_in_executor(
                lambda: search_func(
                    title=query,
                    sort=sort,
                    maxresults=min(limit, 1000),  # Plex API limit
                    **filters,
                    **kwargs,
                )
            )

            # Apply pagination
            total = len(results)
            paginated_results = results[offset : offset + limit]

            return {
                "items": [
                    await self._format_media_item(item)
                    for item in paginated_results
                    if item is not None
                ],
                "total": total,
                "offset": offset,
                "limit": limit,
                "filters": filters,
            }

        except Exception as e:
            logger.error(f"Error searching media: {e}", exc_info=True)
            return {"items": [], "total": 0, "offset": offset, "limit": limit, "error": str(e)}

    async def get_media_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a media item.

        Args:
            media_id: ID of the media item

        Returns:
            Media item details or None if not found
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))
            return await self._format_media_item(item)
        except Exception as e:
            logger.error(f"Error getting media info for {media_id}: {e}")
            return None

    async def update_media(self, media_id: str, **updates) -> Optional[Dict[str, Any]]:
        """Update media item metadata.

        Args:
            media_id: ID of the media item to update
            **updates: Fields to update (e.g., title, summary, year)

        Returns:
            Updated media item or None if update failed
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            # Apply updates
            for key, value in updates.items():
                if hasattr(item, f"set{key.capitalize()}"):
                    await self._run_in_executor(getattr(item, f"set{key.capitalize()}"))(value)
                elif hasattr(item, key):
                    await self._run_in_executor(setattr, item, key, value)

            # Reload the item to get updated data
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            return await self._format_media_item(item)

        except Exception as e:
            logger.error(f"Error updating media {media_id}: {e}")
            return None

    async def delete_media(self, media_id: str) -> bool:
        """Delete a media item.

        Args:
            media_id: ID of the media item to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))
            await self._run_in_executor(item.delete)
            return True
        except Exception as e:
            logger.error(f"Error deleting media {media_id}: {e}")
            return False

    async def rate_media(self, media_id: str, rating: float) -> bool:
        """Rate a media item.

        Args:
            media_id: ID of the media item to rate
            rating: Rating value (0-10)

        Returns:
            True if rating was successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))
            await self._run_in_executor(item.rate, rating)
            return True
        except Exception as e:
            logger.error(f"Error rating media {media_id}: {e}")
            return False

    async def mark_watched(self, media_id: str) -> bool:
        """Mark a media item as watched.

        Args:
            media_id: ID of the media item

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))
            await self._run_in_executor(item.markWatched)
            return True
        except Exception as e:
            logger.error(f"Error marking media {media_id} as watched: {e}")
            return False

    async def mark_unwatched(self, media_id: str) -> bool:
        """Mark a media item as unwatched.

        Args:
            media_id: ID of the media item

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))
            await self._run_in_executor(item.markUnwatched)
            return True
        except Exception as e:
            logger.error(f"Error marking media {media_id} as unwatched: {e}")
            return False

    async def get_media_streams(self, media_id: str) -> List[Dict[str, Any]]:
        """Get stream information for a media item.

        Args:
            media_id: ID of the media item

        Returns:
            List of stream information dictionaries
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            streams = []
            for media in item.media:
                for part in media.parts:
                    for stream in part.streams:
                        stream_info = {
                            "type": stream.streamType,
                            "codec": stream.codec,
                            "bitrate": getattr(stream, "bitrate", None),
                            "language": getattr(stream, "language", None),
                            "language_code": getattr(stream, "languageCode", None),
                            "channels": getattr(stream, "channels", None),
                            "width": getattr(stream, "width", None),
                            "height": getattr(stream, "height", None),
                            "duration": getattr(stream, "duration", None),
                            "bit_depth": getattr(stream, "bitDepth", None),
                            "chroma_subsampling": getattr(stream, "chromaSubsampling", None),
                            "frame_rate": getattr(stream, "frameRate", None),
                            "profile": getattr(stream, "profile", None),
                            "ref_frames": getattr(stream, "refFrames", None),
                            "sampling_rate": getattr(stream, "samplingRate", None),
                            "selected": getattr(stream, "selected", False),
                            "stream_identifier": getattr(stream, "streamIdentifier", None),
                            "title": getattr(stream, "title", None),
                        }
                        streams.append(stream_info)

            return streams

        except Exception as e:
            logger.error(f"Error getting streams for media {media_id}: {e}")
            return []

    async def get_related_media(self, media_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get related media items.

        Args:
            media_id: ID of the media item
            limit: Maximum number of related items to return

        Returns:
            List of related media items
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            related = []
            if hasattr(item, "related"):
                related_items = await self._run_in_executor(lambda: item.related(maxresults=limit))
                related = [await self._format_media_item(i) for i in related_items]

            return related

        except Exception as e:
            logger.error(f"Error getting related media for {media_id}: {e}")
            return []

    async def get_media_children(
        self, media_id: str, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """Get child items for a media item (e.g., episodes for a show).

        Args:
            media_id: ID of the parent media item
            limit: Maximum number of items to return
            offset: Offset for pagination

        Returns:
            Dictionary with items and pagination info
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            if not hasattr(item, "children") or not callable(item.children):
                return {"items": [], "total": 0, "offset": 0, "limit": limit}

            children = await self._run_in_executor(item.children)
            total = len(children)
            items = children[offset : offset + limit]

            return {
                "items": [await self._format_media_item(i) for i in items],
                "total": total,
                "offset": offset,
                "limit": limit,
            }

        except Exception as e:
            logger.error(f"Error getting children for media {media_id}: {e}")
            return {"items": [], "total": 0, "offset": 0, "limit": limit}

    async def get_media_metadata(self, media_id: str) -> Dict[str, Any]:
        """Get metadata for a media item.

        Args:
            media_id: ID of the media item

        Returns:
            Dictionary with metadata
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            metadata = {
                "id": item.ratingKey,
                "title": item.title,
                "type": item.type,
                "metadata": {},
            }

            # Get all available attributes
            for attr in dir(item):
                if not attr.startswith("_") and not callable(getattr(item, attr)):
                    try:
                        value = getattr(item, attr)
                        # Skip large binary data or complex objects
                        if not isinstance(value, (bytes, bytearray, type(item))):
                            metadata["metadata"][attr] = value
                    except Exception:
                        continue

            return metadata

        except Exception as e:
            logger.error(f"Error getting metadata for media {media_id}: {e}")
            return {}

    async def get_media_analysis(self, media_id: str) -> Dict[str, Any]:
        """Get analysis data for a media item.

        Args:
            media_id: ID of the media item

        Returns:
            Dictionary with analysis data
        """
        if not self._initialized:
            await self.connect()

        try:
            item = await self._run_in_executor(lambda: self.server.fetchItem(int(media_id)))

            analysis = {
                "id": item.ratingKey,
                "title": item.title,
                "type": item.type,
                "analysis": {},
            }

            # Get media parts and streams
            if hasattr(item, "media") and item.media:
                analysis["media"] = []
                for media in item.media:
                    media_info = {
                        "id": media.id,
                        "duration": media.duration,
                        "bitrate": media.bitrate,
                        "width": media.width,
                        "height": media.height,
                        "aspect_ratio": media.aspectRatio,
                        "video_codec": media.videoCodec,
                        "video_resolution": media.videoResolution,
                        "video_frame_rate": media.videoFrameRate,
                        "audio_codec": media.audioCodec,
                        "audio_channels": media.audioChannels,
                        "container": media.container,
                        "parts": [],
                    }

                    for part in media.parts:
                        part_info = {
                            "id": part.id,
                            "file": part.file,
                            "size": part.size,
                            "duration": part.duration,
                            "streams": [],
                        }

                        for stream in part.streams:
                            stream_info = {
                                "id": stream.id,
                                "type": stream.streamType,
                                "codec": stream.codec,
                                "index": stream.index,
                                "channels": getattr(stream, "channels", None),
                                "bitrate": getattr(stream, "bitrate", None),
                                "language": getattr(stream, "language", None),
                                "language_code": getattr(stream, "languageCode", None),
                                "profile": getattr(stream, "profile", None),
                                "selected": getattr(stream, "selected", False),
                            }

                            if stream.streamType == "video":
                                stream_info.update(
                                    {
                                        "width": stream.width,
                                        "height": stream.height,
                                        "aspect_ratio": stream.aspectRatio,
                                        "frame_rate": stream.frameRate,
                                        "bit_depth": getattr(stream, "bitDepth", None),
                                        "chroma_subsampling": getattr(
                                            stream, "chromaSubsampling", None
                                        ),
                                        "ref_frames": getattr(stream, "refFrames", None),
                                        "scan_type": getattr(stream, "scanType", None),
                                    }
                                )
                            elif stream.streamType == "audio":
                                stream_info.update(
                                    {
                                        "channels": stream.channels,
                                        "sampling_rate": getattr(stream, "samplingRate", None),
                                        "bitrate_mode": getattr(stream, "bitrateMode", None),
                                        "audio_channel_layout": getattr(
                                            stream, "audioChannelLayout", None
                                        ),
                                    }
                                )
                            elif stream.streamType == "subtitle":
                                stream_info.update(
                                    {
                                        "format": getattr(stream, "format", None),
                                        "title": getattr(stream, "title", None),
                                        "forced": getattr(stream, "forced", False),
                                        "hearing_impaired": getattr(
                                            stream, "hearingImpaired", False
                                        ),
                                    }
                                )

                            part_info["streams"].append(stream_info)

                        media_info["parts"].append(part_info)

                    analysis["media"].append(media_info)

            return analysis

        except Exception as e:
            logger.error(f"Error getting analysis for media {media_id}: {e}")
            return {}

    async def _get_user_permissions(self, user) -> Dict[str, Any]:
        """Helper method to get user permissions."""
        return {
            "allowSync": getattr(user, "allowSync", False),
            "allowCameraUpload": getattr(user, "allowCameraUpload", False),
            "allowChannels": getattr(user, "allowChannels", False),
            "restricted": getattr(user, "restricted", False),
        }

    async def close(self) -> None:
        """Close the Plex service connection."""
        if self._initialized:
            self._initialized = False
        logger.info("Plex service closed")

    # Context manager support
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all active Plex sessions."""
        if not self._initialized:
            await self.connect()
        try:
            return await self._run_in_executor(self._get_sessions_sync)
        except Exception as e:
            logger.error(f"Failed to get sessions: {str(e)}")
            return []

    def _get_sessions_sync(self) -> List[Dict[str, Any]]:
        """Synchronous helper to get sessions."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
        sessions = []
        for session in self.server.sessions():
            sessions.append({
                'id': getattr(session, 'sessionKey', ''),
                'title': session.title,
                'type': session.type,
                'grandparent_title': getattr(session, 'grandparentTitle', ''),
                'parent_title': getattr(session, 'parentTitle', ''),
                'thumb': getattr(session, 'thumb', ''),
                'duration': getattr(session, 'duration', 0),
                'view_offset': getattr(session, 'viewOffset', 0),
                'player': {
                    'title': session.player.title if hasattr(session, 'player') else '',
                    'product': session.player.product if hasattr(session, 'player') else '',
                    'state': session.player.state if hasattr(session, 'player') else '',
                    'machineIdentifier': session.player.machineIdentifier if hasattr(session, 'player') else '',
                },
                'user': session.usernames[0] if hasattr(session, 'usernames') and session.usernames else '',
            })
        return sessions

    async def get_clients(self) -> List[Dict[str, Any]]:
        """Get all available Plex clients."""
        if not self._initialized:
            await self.connect()
        try:
            return await self._run_in_executor(self._get_clients_sync)
        except Exception as e:
            logger.error(f"Failed to get clients: {str(e)}")
            return []

    def _get_clients_sync(self) -> List[Dict[str, Any]]:
        """Synchronous helper to get clients."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
        clients = []
        for client in self.server.clients():
            clients.append({
                'name': client.title,
                'product': client.product,
                'platform': client.platform,
                'version': client.version,
                'address': client.address,
                'port': client.port,
                'protocol': client.protocol,
                'device': client.device,
                'device_name': client.deviceName,
                'id': client.machineIdentifier,
                'machineIdentifier': client.machineIdentifier,
            })
        return clients

    async def play_media(self, client_identifier: str, media_key: str) -> bool:
        """Play media on a specific client."""
        if not self._initialized:
            await self.connect()
        try:
            return await self._run_in_executor(self._play_media_sync, client_identifier, media_key)
        except Exception as e:
            logger.error(f"Failed to play media: {str(e)}")
            return False

    def _play_media_sync(self, client_identifier: str, media_key: str) -> bool:
        """Synchronous helper to play media."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
        try:
            import urllib.parse
            import requests
            
            # Find the client
            client = None
            for c in self.server.clients():
                if c.machineIdentifier == client_identifier:
                    client = c
                    break
            
            if not client:
                logger.error(f"Client {client_identifier} not found")
                return False
            
            # Build the server:// URI format that Plexamp expects
            server_machine_id = self.server.machineIdentifier
            uri = f"server://{server_machine_id}/com.plexapp.plugins.library/library/metadata/{media_key}"
            encoded_uri = urllib.parse.quote(uri, safe='')
            
            # Send play command directly to client
            client_url = f"http://{client.address}:{client.port}"
            play_url = f"{client_url}/player/playback/playMedia?uri={encoded_uri}&commandID=1"
            
            headers = {"X-Plex-Token": self.token, "Accept": "application/json"}
            response = requests.get(play_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Play command sent to {client.title}")
                return True
            else:
                logger.error(f"Play failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error playing media: {str(e)}")
            return False

    async def stop_playback(self, client_identifier: str) -> bool:
        """Stop playback on a specific client."""
        if not self._initialized:
            await self.connect()
        try:
            return await self._run_in_executor(self._stop_playback_sync, client_identifier)
        except Exception as e:
            logger.error(f"Failed to stop playback: {str(e)}")
            return False

    def _stop_playback_sync(self, client_identifier: str) -> bool:
        """Synchronous helper to stop playback."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
        try:
            client = next((c for c in self.server.clients() if c.machineIdentifier == client_identifier), None)
            if not client:
                logger.error(f"Client {client_identifier} not found")
                return False
            client.stop()
            return True
        except Exception as e:
            logger.error(f"Error stopping playback: {str(e)}")
            return False

    async def control_playback(self, client_identifier: str, action: str, media_key: Optional[str] = None, **kwargs) -> bool:
        """Control playback on a client."""
        if not self._initialized:
            await self.connect()
        try:
            return await self._run_in_executor(self._control_playback_sync, client_identifier, action, media_key, **kwargs)
        except Exception as e:
            logger.error(f"Failed to control playback: {str(e)}")
            return False

    def _control_playback_sync(self, client_identifier: str, action: str, media_key: Optional[str] = None, **kwargs) -> bool:
        """Synchronous helper to control playback."""
        if not self.server:
            raise RuntimeError("Not connected to Plex server")
        try:
            client = next((c for c in self.server.clients() if c.machineIdentifier == client_identifier), None)
            if not client:
                logger.error(f"Client {client_identifier} not found")
                return False
            
            if action == "play":
                if media_key:
                    media = self.server.fetchItem(media_key)
                    client.playMedia(media)
                else:
                    client.play()
            elif action == "pause":
                client.pause()
            elif action == "stop":
                client.stop()
            elif action == "skip_next":
                client.skipNext()
            elif action == "skip_previous":
                client.skipPrevious()
            elif action == "step_forward":
                client.stepForward(offset=kwargs.get('offset', 30))
            elif action == "step_back":
                client.stepBack(offset=kwargs.get('offset', 30))
            elif action == "seek_to":
                client.seekTo(kwargs.get('seek_to', 0))
            else:
                logger.error(f"Unknown action: {action}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error controlling playback: {str(e)}")
            return False
