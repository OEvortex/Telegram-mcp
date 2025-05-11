"""
Telegram MCP Tools Package

Contains various tool functions for interacting with Telegram using MCP.
"""

from ..tool_config import get_enabled_tool_modules

# Get enabled modules
enabled_modules = get_enabled_tool_modules()

# Import modules based on configuration
if 'chat' in enabled_modules:
    from . import chat
if 'contacts' in enabled_modules:
    from . import contacts
if 'messages' in enabled_modules:
    from . import messages
if 'groups' in enabled_modules:
    from . import groups
if 'media' in enabled_modules:
    from . import media
if 'profile' in enabled_modules:
    from . import profile
if 'admin' in enabled_modules:
    from . import admin

# Export tool functions from enabled modules
__all__ = []

# Conditionally extend __all__ based on enabled modules
if 'chat' in enabled_modules:
    __all__.extend(chat.__all__)
if 'contacts' in enabled_modules:
    __all__.extend(contacts.__all__)
if 'messages' in enabled_modules:
    __all__.extend(messages.__all__)
if 'groups' in enabled_modules:
    __all__.extend(groups.__all__)
if 'media' in enabled_modules:
    __all__.extend(media.__all__)
if 'profile' in enabled_modules:
    __all__.extend(profile.__all__)
if 'admin' in enabled_modules:
    __all__.extend(admin.__all__)
