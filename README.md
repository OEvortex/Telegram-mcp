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
  <a href="https://deepwiki.com/OEvortex/tgmcp">
    <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
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

# Optional: Tool Configuration
# Control which tool sets are enabled (default is true for all)
# TGMCP_ENABLE_CHAT_TOOLS=true
# TGMCP_ENABLE_CONTACT_TOOLS=true
# TGMCP_ENABLE_MESSAGE_TOOLS=true
# TGMCP_ENABLE_GROUP_TOOLS=true
# TGMCP_ENABLE_MEDIA_TOOLS=true
# TGMCP_ENABLE_PROFILE_TOOLS=true
# TGMCP_ENABLE_ADMIN_TOOLS=true
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
          "MCP_NONINTERACTIVE": "true",
          
          "TGMCP_ENABLE_CHAT_TOOLS": "true",
          "TGMCP_ENABLE_CONTACT_TOOLS": "true",
          "TGMCP_ENABLE_MESSAGE_TOOLS": "true",
          "TGMCP_ENABLE_GROUP_TOOLS": "true",
          "TGMCP_ENABLE_MEDIA_TOOLS": "true",
          "TGMCP_ENABLE_PROFILE_TOOLS": "true",
          "TGMCP_ENABLE_ADMIN_TOOLS": "true"
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
          "MCP_NONINTERACTIVE": "true",
          
          "TGMCP_ENABLE_CHAT_TOOLS": "true",
          "TGMCP_ENABLE_CONTACT_TOOLS": "true",
          "TGMCP_ENABLE_MESSAGE_TOOLS": "true",
          "TGMCP_ENABLE_GROUP_TOOLS": "true",
          "TGMCP_ENABLE_MEDIA_TOOLS": "true",
          "TGMCP_ENABLE_PROFILE_TOOLS": "true",
          "TGMCP_ENABLE_ADMIN_TOOLS": "true"
        }
      }
    }
  }
}
```

### Tool Configuration

TGMCP allows you to selectively enable or disable specific tool sets using environment variables. This can be useful for:
- Reducing the number of available tools for security or simplicity
- Limiting functionality for specific use cases
- Improving performance by loading only necessary components

You can configure which tool sets are enabled by setting the following environment variables:

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `TGMCP_ENABLE_CHAT_TOOLS` | Enable/disable chat-related tools | `true` |
| `TGMCP_ENABLE_CONTACT_TOOLS` | Enable/disable contact management tools | `true` |
| `TGMCP_ENABLE_MESSAGE_TOOLS` | Enable/disable message operation tools | `true` |
| `TGMCP_ENABLE_GROUP_TOOLS` | Enable/disable group administration tools | `true` |
| `TGMCP_ENABLE_MEDIA_TOOLS` | Enable/disable media handling tools | `true` |
| `TGMCP_ENABLE_PROFILE_TOOLS` | Enable/disable profile management tools | `true` |
| `TGMCP_ENABLE_ADMIN_TOOLS` | Enable/disable administrative function tools | `true` |

Set these variables to `true` or `false` to enable or disable the corresponding tool set. For example:

```
# Disable admin and group tools, enable everything else
TGMCP_ENABLE_ADMIN_TOOLS=false
TGMCP_ENABLE_GROUP_TOOLS=false
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
import os
from tgmcp import client, get_tool_config

async def main():
    # Optional: Configure which tools to enable
    # These should be set before importing any tools
    os.environ["TGMCP_ENABLE_ADMIN_TOOLS"] = "false"  # Disable admin tools
    
    # Connect to Telegram
    await client.start()
    
    # Get user info
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} {getattr(me, 'last_name', '')}")
    
    # Send a message
    await client.send_message('username', 'Hello from TGMCP!')
    
    # Check which tool sets are enabled
    tool_config = get_tool_config()
    print("Enabled tool sets:", [k for k, v in tool_config.items() if v])
    
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
- `get_direct_chat_by_contact` - Find a direct chat with a specific contact
- `send_message` - Send text messages to any chat
- `archive_chat` - Archive a chat
- `unarchive_chat` - Unarchive a chat
- `mute_chat` - Mute notifications for a chat
- `unmute_chat` - Unmute notifications for a chat
- `get_invite_link` - Get the invite link for a group or channel
- `export_chat_invite` - Export a chat invite link
- `join_chat_by_link` - Join a chat by invite link
- `import_chat_invite` - Import a chat invite by hash

### Message Operations
- `get_messages` - Get paginated messages from a specific chat
- `list_messages` - List messages with detailed information
- `get_message_context` - Get context around a specific message
- `forward_message` - Forward a message to another chat
- `edit_message` - Edit a previously sent message
- `delete_message` - Delete messages
- `pin_message` - Pin a message in a chat
- `unpin_message` - Unpin a message from a chat
- `mark_as_read` - Mark messages as read
- `reply_to_message` - Reply to a specific message
- `search_messages` - Search for messages in a chat
- `get_pinned_messages` - Get all pinned messages in a chat
- `get_history` - Get chat history with customizable filters

### Contact Management
- `list_contacts` - View all contacts in your Telegram account
- `search_contacts` - Find contacts by name, username, or phone
- `get_contact_ids` - Get contact IDs for specific contacts
- `get_contact_chats` - Get chats with specific contacts
- `get_last_interaction` - Get last interaction with a contact
- `add_contact` - Add new contacts to your Telegram account
- `delete_contact` - Delete contacts from your account
- `block_user` - Block users from contacting you
- `unblock_user` - Unblock previously blocked users
- `import_contacts` - Import multiple contacts at once
- `export_contacts` - Export all contacts to a structured format
- `get_blocked_users` - Get a list of blocked users
- `resolve_username` - Resolve a username to a Telegram entity
- `search_public_chats` - Search for public chats

### Group Administration
- `create_group` - Create new groups and add members
- `create_channel` - Create a new broadcast channel
- `invite_to_group` - Invite users to existing groups
- `leave_chat` - Leave a group or channel
- `get_participants` - List members of a group or channel
- `edit_chat_title` - Change the title of a group or channel
- `edit_chat_photo` - Change the photo of a group or channel
- `delete_chat_photo` - Remove the photo from a group or channel
- `promote_admin` - Give administrator privileges to users
- `demote_admin` - Revoke administrator privileges
- `ban_user` - Ban users from a group or channel
- `unban_user` - Unban previously banned users
- `get_admins` - List administrators of a group or channel
- `get_banned_users` - List banned users
- `get_recent_actions` - Get recent administrative actions

### Media Tools
- `send_file` - Send documents, photos, or videos
- `download_media` - Save media from messages to your device
- `get_media_info` - Get information about media in messages
- `send_voice` - Send voice messages
- `send_sticker` - Send stickers to chats
- `get_sticker_sets` - Get available sticker sets
- `get_gif_search` - Search for GIFs
- `send_gif` - Send GIFs to chats

### Profile Management
- `get_me` - Get information about your own account
- `update_profile` - Update profile information (name, bio)
- `set_profile_photo` - Set a new profile photo
- `delete_profile_photo` - Remove profile photos
- `get_privacy_settings` - Get current privacy settings
- `set_privacy_settings` - Update privacy settings
- `get_user_photos` - Get a user's profile photos
- `get_user_status` - Check a user's online status
- `get_bot_info` - Get information about a bot
- `set_bot_commands` - Configure bot commands



## 📚 Example

```python
import asyncio
import os
from dotenv import load_dotenv
from tgmcp import client, get_tool_config

# Load environment variables
load_dotenv()

# Optional: Configure which tools to enable
# os.environ["TGMCP_ENABLE_ADMIN_TOOLS"] = "false"  # Uncomment to disable admin tools

async def example():
    # Start the client
    await client.start()
    
    # Get recent chats
    dialogs = await client.get_dialogs(limit=5)
    print("\nRecent chats:")
    for dialog in dialogs:
        chat_name = getattr(dialog.entity, "title", None) or getattr(dialog.entity, "first_name", "Unknown")
        print(f"- {chat_name} (ID: {dialog.entity.id})")
    
    # Display which tool sets are enabled
    tool_config = get_tool_config()
    print("\nEnabled tool sets:")
    for tool_set, enabled in tool_config.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"- {tool_set}: {status}")
    
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
