"""
PlexMCP User Management Portmanteau Tool

Consolidates all user-related operations into a single comprehensive interface.
FastMCP 3.2 compliant.
"""

import os
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...models.user import UserRole
from ...utils import get_logger

logger = get_logger(__name__)


def _get_plex_service():
    """Get PlexService instance with proper environment variable handling."""
    from ...services.plex_service import PlexService

    base_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    token = os.getenv("PLEX_TOKEN")

    if not token:
        raise RuntimeError(
            "PLEX_TOKEN environment variable is required. "
            "Get your token from Plex Web App (Settings -> Account -> Authorized Devices) "
            "or visit https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ "
            "for detailed instructions."
        )

    return PlexService(base_url=base_url, token=token)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_user(
    operation: Annotated[
        Literal["list", "get", "create", "update", "delete", "update_permissions"],
        Field(description="User management operation to execute."),
    ],
    user_id: Annotated[str | None, Field(description="Target user ID for scoped operations.")] = None,
    username: Annotated[str | None, Field(description="Username for create/update operations.")] = None,
    email: Annotated[str | None, Field(description="Email address for create/update operations.")] = None,
    password: Annotated[str | None, Field(description="Password for create/update operations (min 8 chars).")] = None,
    role: Annotated[
        Literal["owner", "admin", "user", "managed", "shared"] | None, Field(description="User role assignment.")
    ] = None,
    restricted: Annotated[bool | None, Field(description="Restrict user to specific libraries.")] = None,
    permissions: Annotated[
        dict[str, Any] | None, Field(description="Permission dict with keys like allowSync, restricted.")
    ] = None,
) -> ToolResult:
    """
    Comprehensive user management operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 user and access control operations into a single interface to ensure
    consistent security policy enforcement across shared libraries.

    ## Return Format
    ToolResult with content dict: {"success": bool, "operation": str, "data": {...}}

    ## Examples
    await plex_user(operation="list")
    await plex_user(operation="get", user_id="123")
    await plex_user(operation="create", username="newuser", email="user@example.com", password="secret1234")
    """
    try:
        plex = _get_plex_service()

        if operation == "list":
            users_data = await plex.list_users()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list",
                    "data": users_data,
                    "count": len(users_data),
                }
            )

        if operation == "get":
            if not user_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "user_id is required for get operation",
                        "error_code": "MISSING_USER_ID",
                        "suggestions": ["Use plex_user(operation='list') to find available user IDs"],
                    }
                )

            user_data = await plex.get_user(user_id)
            if user_data is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": f"User {user_id} not found",
                        "error_code": "USER_NOT_FOUND",
                        "suggestions": [
                            "Use plex_user(operation='list') to find valid user IDs",
                            "Verify the user_id is correct",
                        ],
                    }
                )
            return ToolResult(content={"success": True, "operation": "get", "data": user_data})

        if operation == "create":
            if not username:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "username is required for create operation",
                        "error_code": "MISSING_USERNAME",
                        "suggestions": ["Provide username parameter (min 3 characters)"],
                    }
                )
            if not email:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "email is required for create operation",
                        "error_code": "MISSING_EMAIL",
                        "suggestions": ["Provide email parameter (valid email format)"],
                    }
                )
            if not password:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "password is required for create operation",
                        "error_code": "MISSING_PASSWORD",
                        "suggestions": ["Provide password parameter (min 8 characters)"],
                    }
                )

            if len(username) < 3:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "username must be at least 3 characters",
                        "error_code": "INVALID_USERNAME",
                        "suggestions": ["Provide a username with at least 3 characters"],
                    }
                )
            if len(password) < 8:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "password must be at least 8 characters",
                        "error_code": "INVALID_PASSWORD",
                        "suggestions": ["Provide a password with at least 8 characters"],
                    }
                )

            role_str = role.value if isinstance(role, UserRole) else (role or "user")
            user_data = await plex.create_user(
                username=username,
                email=email,
                password=password,
                role=role_str,
                restricted=restricted or False,
            )
            return ToolResult(
                content={
                    "success": True,
                    "operation": "create",
                    "data": user_data,
                }
            )

        if operation == "update":
            if not user_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "user_id is required for update operation",
                        "error_code": "MISSING_USER_ID",
                        "suggestions": ["Provide user_id to update"],
                    }
                )

            update_kwargs = {}
            if username is not None:
                if len(username) < 3:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": "username must be at least 3 characters",
                            "error_code": "INVALID_USERNAME",
                            "suggestions": ["Provide a username with at least 3 characters"],
                        }
                    )
                update_kwargs["username"] = username
            if email is not None:
                update_kwargs["email"] = email
            if password is not None:
                if len(password) < 8:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": "password must be at least 8 characters",
                            "error_code": "INVALID_PASSWORD",
                            "suggestions": ["Provide a password with at least 8 characters"],
                        }
                    )
                update_kwargs["password"] = password
            if role is not None:
                role_str = role.value if isinstance(role, UserRole) else role
                update_kwargs["role"] = role_str
            if restricted is not None:
                update_kwargs["restricted"] = restricted

            if not update_kwargs:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "At least one update field (username, email, password, role, restricted) is required",
                        "error_code": "MISSING_UPDATE_FIELDS",
                        "suggestions": ["Provide at least one field to update"],
                    }
                )

            user_data = await plex.update_user(user_id, **update_kwargs)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "update",
                    "user_id": user_id,
                    "data": user_data,
                }
            )

        if operation == "delete":
            if not user_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "user_id is required for delete operation",
                        "error_code": "MISSING_USER_ID",
                        "suggestions": ["Provide user_id to delete"],
                    }
                )

            result = await plex.delete_user(user_id)
            return ToolResult(
                content={
                    "success": result,
                    "operation": "delete",
                    "user_id": user_id,
                    "data": {"deleted": result},
                }
            )

        if operation == "update_permissions":
            if not user_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "user_id is required for update_permissions operation",
                        "error_code": "MISSING_USER_ID",
                        "suggestions": ["Provide user_id to update permissions"],
                    }
                )
            if not permissions:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "permissions dictionary is required for update_permissions operation",
                        "error_code": "MISSING_PERMISSIONS",
                        "suggestions": [
                            "Provide permissions dict: {'allowSync': True, 'restricted': False}",
                            "Available permission keys: allowSync, allowCameraUpload, allowChannels, restricted",
                        ],
                    }
                )

            result = await plex.update_user_permissions(user_id, permissions)
            user_data = await plex.get_user(user_id)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "update_permissions",
                    "user_id": user_id,
                    "data": user_data or result,
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: list, get, create, update, delete, update_permissions",
                    f"You provided: '{operation}'",
                ],
            }
        )

    except Exception as e:
        error_msg = str(e)
        is_unauthorized = "unauthorized" in error_msg.lower() or "(401)" in error_msg

        logger.exception(
            f"Error in plex_user operation '{operation}': {error_msg}",
            exc_info=not is_unauthorized,
        )

        suggestions = [
            "Check Plex server is running and accessible",
            "Verify your server URL and token in settings",
            "Check server logs for detailed error information",
        ]

        if is_unauthorized:
            suggestions = [
                "Update your PLEX_TOKEN in settings",
                "Verify your token hasn't expired",
                "Visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return ToolResult(
            content={
                "success": False,
                "error": f"Plex Authentication Failed: {error_msg}" if is_unauthorized else error_msg,
                "error_code": "AUTH_FAILURE" if is_unauthorized else "UNEXPECTED_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            }
        )
