"""
Telegram Session String Generator

This module helps to generate a session string for Telegram authentication.
The session string can be used for more robust authentication with Telegram API.
"""

import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def generate_session_string():
    """Generate a session string for Telegram authentication."""
    # Get or prompt for API credentials
    api_id = os.getenv("TELEGRAM_API_ID") or input("Enter your Telegram API ID: ")
    api_hash = os.getenv("TELEGRAM_API_HASH") or input("Enter your Telegram API hash: ")
    
    try:
        api_id = int(api_id)
    except ValueError:
        print(f"Error: API ID must be a number, got '{api_id}'")
        return False
    
    # Create the client with StringSession
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        # Login to Telegram
        print("Please login to your Telegram account to generate a session string.")
        await client.start()
        
        # Generate the session string
        session_string = client.session.save()
        
        # Print the session string
        print("\n---------- BEGIN SESSION STRING ----------")
        print(session_string)
        print("---------- END SESSION STRING ------------\n")
        
        # Save to .env file
        save_to_env = input("Do you want to save this session string to your .env file? (y/n): ").lower()
        if save_to_env == 'y':
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            
            # Read existing .env content
            env_content = ""
            if os.path.exists(env_path):
                with open(env_path, 'r') as env_file:
                    env_content = env_file.read()
            
            # Update or add TELEGRAM_SESSION_STRING
            if "TELEGRAM_SESSION_STRING=" in env_content:
                lines = env_content.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("TELEGRAM_SESSION_STRING="):
                        new_lines.append(f"TELEGRAM_SESSION_STRING={session_string}")
                    else:
                        new_lines.append(line)
                env_content = "\n".join(new_lines)
            else:
                env_content += f"\nTELEGRAM_SESSION_STRING={session_string}\n"
            
            # Write back to .env
            with open(env_path, 'w') as env_file:
                env_file.write(env_content)
            
            print(f"Session string saved to {env_path}")
        
        print("\nIMPORTANT: Keep this session string secure! Anyone with this string can access your Telegram account.")
        print("Add this session string to your MCP configuration in VS Code settings.json:")
        print("""
"mcp-telegram": {
    "command": "tgmcp",
    "args": ["start"],
    "env": {
        "TELEGRAM_API_ID": "your_api_id",
        "TELEGRAM_API_HASH": "your_api_hash",
        "TELEGRAM_SESSION_STRING": "your_session_string",
        "MCP_NONINTERACTIVE": "true"
    }
}
        """)
    
    return True

def main():
    """Run the session string generator."""
    try:
        result = asyncio.run(generate_session_string())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
