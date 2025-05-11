"""
Telegram MCP Tools Package

Contains various tool functions for interacting with Telegram using MCP.
"""

# Import all modules to make them available
from . import chat
from . import contacts
from . import messages
from . import groups
from . import media
from . import profile
from . import admin

# Export all tool functions
__all__ = []
__all__.extend(chat.__all__)
__all__.extend(contacts.__all__)
__all__.extend(messages.__all__)
__all__.extend(groups.__all__)
__all__.extend(media.__all__)
__all__.extend(profile.__all__)
__all__.extend(admin.__all__)
