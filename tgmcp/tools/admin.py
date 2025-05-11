"""
Admin and advanced management tool functions for Telegram MCP.

Functions for administrative operations.
"""

import json
from ..client import client, mcp
from ..utils import log_and_format_error, json_serializer

__all__ = [
    'leave_chat',  # Also included in groups.py but makes sense here too
    'export_chat_invite',
    'import_chat_invite',
    'get_recent_actions'
]

# These functions are already defined in other modules
# but can be imported here for administrative convenience
from ..tools.groups import leave_chat, get_recent_actions
from ..tools.chat import export_chat_invite, import_chat_invite
