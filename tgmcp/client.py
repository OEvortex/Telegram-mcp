"""
Telegram Client Setup and Configuration

This module handles the setup and initialization of the Telegram client.
"""

import os
import sys
import logging
import sqlite3
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Load tool configuration environment variables
# This ensures they're loaded before any tool imports

# Setup logging first
logger = logging.getLogger("telegram_mcp")
logger.setLevel(logging.ERROR)  # Set to ERROR for production, INFO for debugging

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Set to ERROR for production, INFO for debugging

# Create formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Initialize the MCP server
mcp = FastMCP("telegram")

# Telegram API credentials
try:
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
except ValueError:
    logger.error(f"Invalid API ID format. Got: '{os.getenv('TELEGRAM_API_ID')}'")
    logger.error("Please make sure TELEGRAM_API_ID is a valid number")
    sys.exit(1)

TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "tgmcp_session")

# Check if a string session exists in environment, otherwise use file-based session
SESSION_STRING = os.getenv("TELEGRAM_SESSION_STRING")

# Initialize Telegram client
if SESSION_STRING:
    # Use the string session if available
    client = TelegramClient(StringSession(SESSION_STRING), TELEGRAM_API_ID, TELEGRAM_API_HASH)
else:
    # Use file-based session
    client = TelegramClient(TELEGRAM_SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# Create file handler with absolute path for logging
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, "mcp_errors.log")

try:
    file_handler = logging.FileHandler(log_file_path, mode="a")  # Append mode
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f"Logging initialized to {log_file_path}")
except Exception as log_error:
    logger.warning(f"Error setting up log file: {log_error}")
    # Fallback to console-only logging
    logger.error(f"Failed to set up log file handler: {log_error}")
