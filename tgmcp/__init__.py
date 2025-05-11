"""
Telegram MCP (Model Context Protocol) Package

A package for interacting with Telegram using the Model Context Protocol.
"""

__version__ = "0.1.0"

# Import the most important components for easier access
from .client import client, mcp
from .utils import format_entity, format_message, log_and_format_error
from .tool_config import get_enabled_tool_modules, get_tool_config

# Import tools based on configuration
enabled_modules = get_enabled_tool_modules()

# Conditionally import tools based on configuration
if 'chat' in enabled_modules:
    from .tools.chat import *
if 'contacts' in enabled_modules:
    from .tools.contacts import *
if 'messages' in enabled_modules:
    from .tools.messages import *
if 'groups' in enabled_modules:
    from .tools.groups import *
if 'media' in enabled_modules:
    from .tools.media import *
if 'profile' in enabled_modules:
    from .tools.profile import *
if 'admin' in enabled_modules:
    from .tools.admin import *

# Version info
__all__ = ['__version__', 'client', 'mcp', 'get_tool_config']
