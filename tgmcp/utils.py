"""
Utility functions for the Telegram MCP package.

This module contains utility functions for error handling, entity formatting, etc.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from telethon import utils
from telethon.tl.types import User, Chat, Channel

from .client import logger

# Error code prefix mapping for better error tracing
ERROR_PREFIXES = {
    "chat": "CHAT",
    "msg": "MSG",
    "contact": "CONTACT",
    "group": "GROUP",
    "media": "MEDIA",
    "profile": "PROFILE",
    "auth": "AUTH",
    "admin": "ADMIN",
}


def json_serializer(obj):
    """Helper function to convert non-serializable objects for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    # Add other non-serializable types as needed
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def log_and_format_error(
    function_name: str, error: Exception, prefix: str = None, **kwargs
) -> str:
    """
    Centralized error handling function that logs the error and returns a formatted user-friendly message.

    Args:
        function_name: Name of the function where error occurred
        error: The exception that was raised
        prefix: Error code prefix (e.g., "CHAT", "MSG") - if None, will be derived from function_name
        **kwargs: Additional context parameters to include in log

    Returns:
        A user-friendly error message with error code
    """
    # Generate a consistent error code
    if prefix is None:
        # Try to derive prefix from function name
        for key, value in ERROR_PREFIXES.items():
            if key in function_name.lower():
                prefix = value
                break
        if prefix is None:
            prefix = "GEN"  # Generic prefix if none matches

    error_code = f"{prefix}-ERR-{abs(hash(function_name)) % 1000:03d}"

    # Format the additional context parameters
    context = ", ".join(f"{k}={v}" for k, v in kwargs.items())

    # Log the full technical error
    logger.exception(f"{function_name} failed ({context}): {error}")

    # Return a user-friendly message
    return f"An error occurred (code: {error_code}). Check mcp_errors.log for details."


def format_entity(entity) -> Dict[str, Any]:
    """Helper function to format entity information consistently."""
    result = {"id": entity.id}

    if hasattr(entity, "title"):
        result["name"] = entity.title
        result["type"] = "group" if isinstance(entity, Chat) else "channel"
    elif hasattr(entity, "first_name"):
        name_parts = []
        if entity.first_name:
            name_parts.append(entity.first_name)
        if hasattr(entity, "last_name") and entity.last_name:
            name_parts.append(entity.last_name)
        result["name"] = " ".join(name_parts)
        result["type"] = "user"
        if hasattr(entity, "username") and entity.username:
            result["username"] = entity.username
        if hasattr(entity, "phone") and entity.phone:
            result["phone"] = entity.phone

    return result


def format_message(message) -> Dict[str, Any]:
    """Helper function to format message information consistently."""
    result = {
        "id": message.id,
        "date": message.date.isoformat(),
        "text": message.message or "",
    }

    if message.from_id:
        result["from_id"] = utils.get_peer_id(message.from_id)

    if message.media:
        result["has_media"] = True
        result["media_type"] = type(message.media).__name__

    return result
