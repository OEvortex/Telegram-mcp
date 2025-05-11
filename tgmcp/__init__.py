"""
Telegram MCP (Model Context Protocol) Package

A package for interacting with Telegram using the Model Context Protocol.
"""

__version__ = "0.1.0"

# Import the most important components for easier access
from .client import client, mcp
from .utils import format_entity, format_message, log_and_format_error

# Import all tools for easy access
from .tools.chat import *
from .tools.contacts import *
from .tools.messages import *
from .tools.groups import *
from .tools.media import *
from .tools.profile import *
from .tools.admin import *

# Version info
__all__ = ['__version__', 'client', 'mcp']
