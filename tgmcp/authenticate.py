"""
Telegram Authentication Module

This module provides authentication functionality for the Telegram client.
"""

import asyncio
import os
import sys
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from .client import client

async def authenticate():
    """Authenticate the Telegram client interactively."""
    print("Starting Telegram authentication...")
    
    # Connect to client
    await client.connect()
    
    # Check if already authenticated
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already authenticated as: {me.first_name} (@{me.username or 'no username'})")
        return True
    
    # If not authenticated, start interactive login
    print("Authentication required. Please login:")
    phone = input("Enter your phone number (with country code, e.g. +1234567890): ")
    
    # Send code request
    try:
        await client.send_code_request(phone)
        code = input("Enter the verification code sent to your phone: ")
    except Exception as e:
        print(f"Error requesting verification code: {e}")
        await client.disconnect()
        return False
    
    try:
        # Try to sign in with the code
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        # 2FA is enabled, ask for password
        password = input("Two-factor authentication is enabled. Enter your password: ")
        await client.sign_in(password=password)
    except Exception as e:
        print(f"Sign-in error: {e}")
        await client.disconnect()
        return False
    
    me = await client.get_me()
    print(f"Authentication successful! Logged in as: {me.first_name} (@{me.username or 'no username'})")
    
    # Get the session file path
    session_name = os.getenv("TELEGRAM_SESSION_NAME", "tgmcp_session")
    print(f"Session saved to: {session_name}.session")
    
    # Generate session string
    session_string = client.session.save()
    print("\nSession string (for VS Code settings):")
    print("---------- BEGIN SESSION STRING ----------")
    print(session_string)
    print("---------- END SESSION STRING ------------")
    print("\nIMPORTANT: Store this session string in your VS Code settings for more reliable authentication.")
    
    # Disconnect the client
    await client.disconnect()
    return True

def main():
    """Run the authentication process."""
    try:
        result = asyncio.run(authenticate())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\nAuthentication cancelled by user.")
        return 1
    except Exception as e:
        print(f"Authentication error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
