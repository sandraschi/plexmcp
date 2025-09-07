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
    try:
        user_data = await plex.create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role.value,  # Convert enum to string
            restricted=request.restricted
        )
        return User(**user_data)
    except Exception as e:
        logger.error(f"Failed to create user {request.username}: {e}")
        raise

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
        Updated user information
    """
    try:
        update_data = {}
        if request.username is not None:
            update_data['username'] = request.username
        if request.email is not None:
            update_data['email'] = request.email
        if request.password is not None:
            update_data['password'] = request.password
        if request.role is not None:
            update_data['role'] = request.role.value  # Convert enum to string
        if request.restricted is not None:
            update_data['restricted'] = request.restricted
            
        user_data = await plex.update_user(
            user_id=request.user_id,
            **update_data
        )
        return User(**user_data)
    except Exception as e:
        logger.error(f"Failed to update user {request.user_id}: {e}")
        raise

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
    try:
        success = await plex.delete_user(user_id=request.user_id)
        if success:
            logger.info(f"Successfully deleted user {request.user_id}")
        else:
            logger.warning(f"Failed to delete user {request.user_id}")
        return success
    except Exception as e:
        logger.error(f"Error deleting user {request.user_id}: {e}")
        return False

@mcp_tool("plex.users.list")
async def list_users(plex: PlexService) -> UserList:
    """List all Plex users.
    
    Returns:
        List of all users with their information
    """
    try:
        users_data = await plex.list_users()
        users = [User(**user_data) for user_data in users_data]
        return UserList(users=users)
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return UserList(users=[])

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
    try:
        user_data = await plex.get_user(user_id=request.user_id)
        if user_data:
            return User(**user_data)
        return None
    except Exception as e:
        logger.error(f"Error getting user {request.user_id}: {e}")
        return None

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
    try:
        result = await plex.update_user_permissions(
            user_id=request.user_id,
            permissions=request.permissions
        )
        # Get the updated user data
        user_data = await plex.get_user(user_id=request.user_id)
        if not user_data:
            raise ValueError(f"User {request.user_id} not found after updating permissions")
        return User(**user_data)
    except Exception as e:
        logger.error(f"Error updating permissions for user {request.user_id}: {e}")
        raise
