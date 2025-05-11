"""
Main entry point for the Telegram MCP package.

This module provides the main entry point for running the Telegram MCP package.
"""

import sys
import asyncio
import sqlite3
import os
import nest_asyncio
from telethon.errors import SessionPasswordNeededError
from .client import client, mcp, logger

def main():
    """Main entry point for the Telegram MCP package."""
    nest_asyncio.apply()
    
    async def async_main() -> None:
        try:
            # Check if API credentials are valid
            api_id = os.getenv("TELEGRAM_API_ID", "0")
            api_hash = os.getenv("TELEGRAM_API_HASH", "")
            session_string = os.getenv("TELEGRAM_SESSION_STRING", "")
            
            if api_id == "0" or api_id == "<your_api_id>" or not api_hash or api_hash == "<your_api_hash>":
                print("ERROR: Invalid Telegram API credentials", file=sys.stderr)
                print("Please set valid TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables", file=sys.stderr)
                print("You can obtain these from https://my.telegram.org/auth", file=sys.stderr)
                sys.exit(1)
            
            # Start the Telethon client
            logger.info("Starting Telegram client...")
            
            # Connect first before checking authorization
            logger.info("Connecting to Telegram servers...")
            try:
                await client.connect()
            except Exception as e:
                logger.error(f"Connection error: {e}")
                print("Make sure you have internet connectivity and your API credentials are correct", file=sys.stderr)
                sys.exit(1)
            
            # Check if we're authorized
            try:
                is_authorized = await client.is_user_authorized()
            except Exception as e:
                logger.error(f"Authorization check error: {e}")
                
                # If session string is available, suggest regenerating it
                if session_string:
                    print("Your session string may be invalid. Please regenerate it using session_string_generator.py", file=sys.stderr)
                else:
                    print("Your session file may be corrupted. Please authenticate again using authenticate.py", file=sys.stderr)
                
                sys.exit(1)
            
            # If not authorized and this is running in non-interactive mode (MCP server)
            if not is_authorized:
                if os.getenv("MCP_NONINTERACTIVE", ""):
                    print("Authentication required but running in non-interactive mode.", file=sys.stderr)
                    print("Please run authenticate.py or session_string_generator.py first", file=sys.stderr)
                    sys.exit(1)
                
                # For interactive sessions, try to authenticate
                print("First-time authentication required. Please run one of these commands in your terminal:")
                print("1. python -m tgmcp.authenticate")
                print("2. python -m tgmcp.session_string_generator (recommended)")
                print("Then update your settings with the session string")
                sys.exit(1)
            
            # Successfully authenticated
            try:
                user = await client.get_me()
                logger.info(f"Logged in as {user.first_name}")
                logger.info("Telegram client started. Running MCP server...")
                
                # Use the asynchronous entrypoint
                await mcp.run_stdio_async()
            except Exception as e:
                logger.error(f"Error while running MCP server: {e}")
                sys.exit(1)
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            if isinstance(e, sqlite3.OperationalError) and "database is locked" in str(e):
                print(
                    "Database lock detected. Please ensure no other instances are running.",
                    file=sys.stderr,
                )
            sys.exit(1)

    asyncio.run(async_main())


if __name__ == "__main__":
    main()
