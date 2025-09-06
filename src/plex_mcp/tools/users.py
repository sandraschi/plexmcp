"""Plex user management tools for FastMCP 2.10.1."""
from typing import List, Optional

from fastmcp import MCPTool, mcp_tool
from pydantic import BaseModel, Field, EmailStr

from ..models.user import User, UserList, UserRole
from ..services.plex_service import PlexService

class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Username for the new user")
    email: EmailStr = Field(..., description="Email address for the new user")
    password: str = Field(..., min_length=8, description="Password for the new user")
    role: UserRole = Field(UserRole.USER, description="User role (admin, user, managed, shared)")
    restricted: bool = Field(False, description="Whether the user should be restricted")

@mcp_tool("plex.users.create")
async def create_user(plex: PlexService, request: CreateUserRequest) -> User:
    """Create a new Plex user.
    
    Args:
        request: User creation parameters
        
    Returns:
        The created user information
    """
    return await plex.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role,
        restricted=request.restricted
    )

class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""
    user_id: str = Field(..., description="ID of the user to update")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    role: Optional[UserRole] = Field(None, description="New user role")
    restricted: Optional[bool] = Field(None, description="Whether the user should be restricted")

@mcp_tool("plex.users.update")
async def update_user(plex: PlexService, request: UpdateUserRequest) -> User:
    """Update an existing Plex user.
    
    Args:
        request: User update parameters
        
    Returns:
        The updated user information
    """
    return await plex.update_user(
        user_id=request.user_id,
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role,
        restricted=request.restricted
    )

class DeleteUserRequest(BaseModel):
    """Request model for deleting a user."""
    user_id: str = Field(..., description="ID of the user to delete")

@mcp_tool("plex.users.delete")
async def delete_user(plex: PlexService, request: DeleteUserRequest) -> bool:
    """Delete a Plex user.
    
    Args:
        request: User deletion parameters
        
    Returns:
        True if deletion was successful, False otherwise
    """
    return await plex.delete_user(user_id=request.user_id)

@mcp_tool("plex.users.list")
async def list_users(plex: PlexService) -> UserList:
    """List all Plex users.
    
    Returns:
        List of all users with their information
    """
    return await plex.list_users()

class GetUserRequest(BaseModel):
    """Request model for getting a specific user."""
    user_id: str = Field(..., description="ID of the user to retrieve")

@mcp_tool("plex.users.get")
async def get_user(plex: PlexService, request: GetUserRequest) -> Optional[User]:
    """Get a specific Plex user by ID.
    
    Args:
        request: User retrieval parameters
        
    Returns:
        User information if found, None otherwise
    """
    return await plex.get_user(user_id=request.user_id)

class UpdateUserPermissionsRequest(BaseModel):
    """Request model for updating user permissions."""
    user_id: str = Field(..., description="ID of the user to update")
    permissions: dict = Field(..., description="Dictionary of permissions to update")

@mcp_tool("plex.users.update_permissions")
async def update_user_permissions(plex: PlexService, request: UpdateUserPermissionsRequest) -> User:
    """Update permissions for a Plex user.
    
    Args:
        request: Permission update parameters
        
    Returns:
        Updated user information with new permissions
    """
    return await plex.update_user_permissions(
        user_id=request.user_id,
        permissions=request.permissions
    )
