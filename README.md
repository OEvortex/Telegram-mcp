# TGMCP - Telegram Model Context Protocol

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/240px-Telegram_logo.svg.png" alt="Telegram Logo" width="120"/>
  <br>
  <b>Connect AI agents with Telegram using MCP standard</b>
  <br><br>
  <a href="https://pypi.org/project/tgmcp/">
    <img src="https://img.shields.io/pypi/v/tgmcp.svg" alt="PyPI version">
  </a>
  <a href="https://github.com/OEvortex/tgmcp/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/OEvortex/tgmcp" alt="License">
  </a>
  <a href="https://github.com/anthropics/anthropic-cookbook/tree/main/model_context_protocol">
    <img src="https://img.shields.io/badge/protocol-MCP-blue" alt="MCP Protocol">
  </a>
</div>

## 📖 Overview

TGMCP is a Python package that implements the [Model Context Protocol (MCP)](https://github.com/anthropics/anthropic-cookbook/tree/main/model_context_protocol) for Telegram. It allows AI agents to seamlessly interact with Telegram accounts, providing access to messaging, contacts, groups, media sharing, and more.

This package acts as a bridge between AI assistants and Telegram, enabling them to:
- Read and send messages
- Manage contacts and groups
- Handle media (images, documents, stickers, GIFs)
- Perform administrative functions
- Update profile information

All data is handled locally and securely through the Telegram API.

## ✨ Key Features

- **Chat Operations**: List chats, retrieve messages, send messages
- **Contact Management**: Add, delete, block/unblock, search contacts
- **Group Administration**: Create groups, add members, manage permissions
- **Media Handling**: Send/receive files, stickers, GIFs, voice messages
- **Profile Management**: Update profile info, privacy settings
- **Message Operations**: Forward, edit, delete, pin messages
- **Administrative Functions**: Promote/demote admins, ban users

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install tgmcp
```

### From Source
```bash
# Clone the repository
git clone https://github.com/OEvortex/tgmcp.git
cd tgmcp

# Install with pip
pip install -e .
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project directory with your Telegram API credentials:

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_NAME=your_session_name
# Optional: Use string session instead of file session
# TELEGRAM_SESSION_STRING=your_session_string
```

### MCP Configuration

To use TGMCP with VS Code or other MCP-compatible applications, add it to your MCP configuration:

#### Option 1: Using Session String (Recommended)
```json
{
  "mcp": {
    "servers": {
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
    }
  }
}
```

**IMPORTANT**: 
1. Replace `your_api_id`, `your_api_hash`, and `your_session_string` with your actual Telegram API credentials.
2. For most reliable operation, use the session string method (Option 1).
3. The `MCP_NONINTERACTIVE` setting prevents interactive prompts during startup.

#### Option 2: Using Session Files (Basic Method)
```json
{
  "mcp": {
    "servers": {
      "mcp-telegram": {
        "command": "tgmcp",
        "args": ["start"],
        "env": {
          "TELEGRAM_API_ID": "your_api_id",
          "TELEGRAM_API_HASH": "your_api_hash",
          "TELEGRAM_SESSION_NAME": "your_session_name",
          "MCP_NONINTERACTIVE": "true"
        }
      }
    }
  }
}
```

### First-Time Authentication

Before using TGMCP, you need to authenticate with Telegram. You can do this in two ways:

#### Option 1: Generate a Session String (Recommended)
```bash
# Run the session string generator
python -m tgmcp.session_string_generator
```

This will generate a session string that you can use in your MCP configuration. This method is more reliable and portable, especially for cloud environments.

#### Option 2: Use File-Based Authentication
```bash
# Run the authentication script
python -m tgmcp.authenticate
```

This will create a `.session` file that TGMCP will use for authentication.

## 🔍 Usage

### Run as MCP Server
```bash
python -m tgmcp
```

### Use in Your Code
```python
import asyncio
from tgmcp import client

async def main():
    # Connect to Telegram
    await client.start()
    
    # Get user info
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} {getattr(me, 'last_name', '')}")
    
    # Send a message
    await client.send_message('username', 'Hello from TGMCP!')
    
    # Disconnect when done
    await client.disconnect()

asyncio.run(main())
```

## 🛠️ Available MCP Tools

TGMCP provides a comprehensive set of tools that can be utilized through the MCP protocol:

### Chat Tools
- `get_chats` - List available chats with pagination
- `list_chats` - Detailed metadata for users, groups, and channels
- `get_chat` - Information about a specific chat
- `send_message` - Send text messages to any chat

### Contact Management
- `list_contacts` - View all contacts in your Telegram account
- `search_contacts` - Find contacts by name, username, or phone
- `add_contact` - Add new contacts to your Telegram account
- `block_user` - Block users from contacting you

### Group Administration
- `create_group` - Create new groups and add members
- `invite_to_group` - Invite users to existing groups
- `get_participants` - List members of a group or channel
- `promote_admin` - Give administrator privileges to users

### Media Tools
- `send_file` - Send documents, photos, or videos
- `download_media` - Save media from messages to your device
- `send_sticker` - Send stickers to chats
- `send_voice` - Send voice messages

A full list of available tools and their parameters can be found in the [documentation](https://github.com/OEvortex/tgmcp/blob/main/README.md#%EF%B8%8F-tools-available).

## 📚 Example

```python
import asyncio
import os
from dotenv import load_dotenv
from tgmcp import client

# Load environment variables
load_dotenv()

async def example():
    # Start the client
    await client.start()
    
    # Get recent chats
    dialogs = await client.get_dialogs(limit=5)
    print("\nRecent chats:")
    for dialog in dialogs:
        chat_name = getattr(dialog.entity, "title", None) or getattr(dialog.entity, "first_name", "Unknown")
        print(f"- {chat_name} (ID: {dialog.entity.id})")
    
    # Disconnect when done
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(example())
```

## 🔒 Security & Privacy

- All data remains on your local machine
- Authentication with Telegram is handled securely
- No data is sent to third parties
- Session files should be kept secure

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

[MIT License](LICENSE)

## 📞 Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/OEvortex/tgmcp/issues).

## 📦 PyPI Package

This package is available on PyPI:
- https://pypi.org/project/tgmcp/

You can install it using pip:
```bash
pip install tgmcp
```

---

<div align="center">
  <p>Made with ❤️ for AI-assisted Telegram interaction</p>
</div>
