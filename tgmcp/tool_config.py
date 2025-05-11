"""
Tool Configuration Module for Telegram MCP

This module handles the configuration of which tool sets are enabled based on environment variables.
"""

import os
from typing import Dict, Set

# Default configuration - all tools enabled by default
DEFAULT_TOOL_CONFIG = {
    "chat_tools": True,
    "contact_tools": True,
    "message_tools": True,
    "group_tools": True,
    "media_tools": True,
    "profile_tools": True,
    "admin_tools": True,
}

def get_tool_config() -> Dict[str, bool]:
    """
    Get the current tool configuration based on environment variables.
    
    Environment variables should be in the format:
    TGMCP_ENABLE_CHAT_TOOLS=true|false
    TGMCP_ENABLE_CONTACT_TOOLS=true|false
    etc.
    
    Returns:
        Dict[str, bool]: Dictionary of tool categories and their enabled status
    """
    config = DEFAULT_TOOL_CONFIG.copy()
    
    # Map environment variable names to config keys
    env_var_map = {
        "TGMCP_ENABLE_CHAT_TOOLS": "chat_tools",
        "TGMCP_ENABLE_CONTACT_TOOLS": "contact_tools",
        "TGMCP_ENABLE_MESSAGE_TOOLS": "message_tools",
        "TGMCP_ENABLE_GROUP_TOOLS": "group_tools",
        "TGMCP_ENABLE_MEDIA_TOOLS": "media_tools",
        "TGMCP_ENABLE_PROFILE_TOOLS": "profile_tools",
        "TGMCP_ENABLE_ADMIN_TOOLS": "admin_tools",
    }
    
    # Update config based on environment variables
    for env_var, config_key in env_var_map.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            config[config_key] = env_value.lower() in ('true', 't', '1', 'yes', 'y')
    
    return config

def get_enabled_tool_modules() -> Set[str]:
    """
    Get the set of enabled tool modules based on the current configuration.
    
    Returns:
        Set[str]: Set of enabled tool module names
    """
    config = get_tool_config()
    enabled_modules = set()
    
    # Map config keys to module names
    module_map = {
        "chat_tools": "chat",
        "contact_tools": "contacts",
        "message_tools": "messages",
        "group_tools": "groups",
        "media_tools": "media",
        "profile_tools": "profile",
        "admin_tools": "admin",
    }
    
    # Add enabled modules to the set
    for config_key, module_name in module_map.items():
        if config.get(config_key, True):  # Default to True if not specified
            enabled_modules.add(module_name)
    
    return enabled_modules