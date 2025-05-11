"""
Contact management tool functions for Telegram MCP.

Functions for listing, managing, and interacting with contacts.
"""

import json
from telethon.tl.types import User
from telethon.tl.functions.contacts import GetContactsRequest, ImportContactsRequest, ResolveUsernameRequest
from telethon import functions
from telethon.tl.types import User, Chat, Channel
from ..client import client, mcp
from ..utils import log_and_format_error, format_entity, json_serializer

__all__ = [
    'list_contacts',
    'search_contacts',
    'get_contact_ids',
    'get_contact_chats',
    'get_last_interaction',
    'add_contact',
    'delete_contact',
    'block_user',
    'unblock_user',
    'import_contacts',
    'export_contacts',
    'get_blocked_users',
    'resolve_username',
    'search_public_chats'
]

@mcp.tool()
async def list_contacts() -> str:
    """
    List all contacts in your Telegram account.
    """
    try:
        result = await client(GetContactsRequest(hash=0))
        users = result.users
        if not users:
            return "No contacts found."
        lines = []
        for user in users:
            name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
            username = getattr(user, "username", "")
            phone = getattr(user, "phone", "")
            contact_info = f"ID: {user.id}, Name: {name}"
            if username:
                contact_info += f", Username: @{username}"
            if phone:
                contact_info += f", Phone: {phone}"
            lines.append(contact_info)
        return "\n".join(lines)
    except Exception as e:
        return log_and_format_error("list_contacts", e)


@mcp.tool()
async def search_contacts(query: str) -> str:
    """
    Search for contacts by name, username, or phone number using Telethon's SearchRequest.
    Args:
        query: The search term to look for in contact names, usernames, or phone numbers.
    """
    try:
        result = await client(functions.contacts.SearchRequest(q=query, limit=50))
        users = result.users
        if not users:
            return f"No contacts found matching '{query}'."
        lines = []
        for user in users:
            name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
            username = getattr(user, "username", "")
            phone = getattr(user, "phone", "")
            contact_info = f"ID: {user.id}, Name: {name}"
            if username:
                contact_info += f", Username: @{username}"
            if phone:
                contact_info += f", Phone: {phone}"
            lines.append(contact_info)
        return "\n".join(lines)
    except Exception as e:
        return log_and_format_error("search_contacts", e, query=query)


@mcp.tool()
async def get_contact_ids() -> str:
    """
    Get all contact IDs in your Telegram account.
    """
    try:
        result = await client(functions.contacts.GetContactIDsRequest(hash=0))
        if not result:
            return "No contact IDs found."
        return "Contact IDs: " + ", ".join(str(cid) for cid in result)
    except Exception as e:
        return log_and_format_error("get_contact_ids", e)


@mcp.tool()
async def get_contact_chats(contact_id: int) -> str:
    """
    List all chats involving a specific contact.

    Args:
        contact_id: The ID of the contact.
    """
    try:
        # Get contact info
        contact = await client.get_entity(contact_id)
        if not isinstance(contact, User):
            return f"ID {contact_id} is not a user/contact."

        contact_name = (
            f"{getattr(contact, 'first_name', '')} {getattr(contact, 'last_name', '')}".strip()
        )

        # Find direct chat
        direct_chat = None
        dialogs = await client.get_dialogs()

        results = []

        # Look for direct chat
        for dialog in dialogs:
            if isinstance(dialog.entity, User) and dialog.entity.id == contact_id:
                chat_info = f"Direct Chat ID: {dialog.entity.id}, Type: Private"
                if dialog.unread_count:
                    chat_info += f", Unread: {dialog.unread_count}"
                results.append(chat_info)
                break

        # Look for common groups/channels
        common_chats = []
        try:
            common = await client.get_common_chats(contact)
            for chat in common:
                chat_type = "Channel" if getattr(chat, "broadcast", False) else "Group"
                chat_info = f"Chat ID: {chat.id}, Title: {chat.title}, Type: {chat_type}"
                results.append(chat_info)
        except:
            results.append("Could not retrieve common groups.")

        if not results:
            return f"No chats found with {contact_name} (ID: {contact_id})."

        return f"Chats with {contact_name} (ID: {contact_id}):\n" + "\n".join(results)
    except Exception as e:
        return log_and_format_error("get_contact_chats", e, contact_id=contact_id)


@mcp.tool()
async def get_last_interaction(contact_id: int) -> str:
    """
    Get the most recent message with a contact.

    Args:
        contact_id: The ID of the contact.
    """
    try:
        # Get contact info
        contact = await client.get_entity(contact_id)
        if not isinstance(contact, User):
            return f"ID {contact_id} is not a user/contact."

        contact_name = (
            f"{getattr(contact, 'first_name', '')} {getattr(contact, 'last_name', '')}".strip()
        )

        # Get the last few messages
        messages = await client.get_messages(contact, limit=5)

        if not messages:
            return f"No messages found with {contact_name} (ID: {contact_id})."

        results = [f"Last interactions with {contact_name} (ID: {contact_id}):"]

        for msg in messages:
            sender = "You" if msg.out else contact_name
            message_text = msg.message or "[Media/No text]"
            results.append(f"Date: {msg.date}, From: {sender}, Message: {message_text}")

        return "\n".join(results)
    except Exception as e:
        return log_and_format_error("get_last_interaction", e, contact_id=contact_id)


@mcp.tool()
async def add_contact(phone: str, first_name: str, last_name: str = "") -> str:
    """
    Add a new contact to your Telegram account.
    Args:
        phone: The phone number of the contact (with country code).
        first_name: The contact's first name.
        last_name: The contact's last name (optional).
    """
    try:
        # Try to import the required types first
        from telethon.tl.types import InputPhoneContact

        result = await client(
            ImportContactsRequest(
                contacts=[
                    InputPhoneContact(
                        client_id=0, phone=phone, first_name=first_name, last_name=last_name
                    )
                ]
            )
        )
        if result.imported:
            return f"Contact {first_name} {last_name} added successfully."
        else:
            return f"Contact not added. Response: {str(result)}"
    except (ImportError, AttributeError) as type_err:
        # Try alternative approach using raw API
        try:
            result = await client(
                ImportContactsRequest(
                    contacts=[
                        {
                            "client_id": 0,
                            "phone": phone,
                            "first_name": first_name,
                            "last_name": last_name,
                        }
                    ]
                )
            )
            if hasattr(result, "imported") and result.imported:
                return f"Contact {first_name} {last_name} added successfully (alt method)."
            else:
                return f"Contact not added. Alternative method response: {str(result)}"
        except Exception as alt_e:
            return log_and_format_error("add_contact", alt_e, phone=phone)
    except Exception as e:
        return log_and_format_error("add_contact", e, phone=phone)


@mcp.tool()
async def delete_contact(user_id: int) -> str:
    """
    Delete a contact by user ID.
    Args:
        user_id: The Telegram user ID of the contact to delete.
    """
    try:
        user = await client.get_entity(user_id)
        await client(functions.contacts.DeleteContactsRequest(id=[user]))
        return f"Contact with user ID {user_id} deleted."
    except Exception as e:
        return log_and_format_error("delete_contact", e, user_id=user_id)


@mcp.tool()
async def block_user(user_id: int) -> str:
    """
    Block a user by user ID.
    Args:
        user_id: The Telegram user ID to block.
    """
    try:
        user = await client.get_entity(user_id)
        await client(functions.contacts.BlockRequest(id=user))
        return f"User {user_id} blocked."
    except Exception as e:
        return log_and_format_error("block_user", e, user_id=user_id)


@mcp.tool()
async def unblock_user(user_id: int) -> str:
    """
    Unblock a user by user ID.
    Args:
        user_id: The Telegram user ID to unblock.
    """
    try:
        user = await client.get_entity(user_id)
        await client(functions.contacts.UnblockRequest(id=user))
        return f"User {user_id} unblocked."
    except Exception as e:
        return log_and_format_error("unblock_user", e, user_id=user_id)


@mcp.tool()
async def import_contacts(contacts: list) -> str:
    """
    Import a list of contacts. Each contact should be a dict with phone, first_name, last_name.
    """
    try:
        input_contacts = [
            functions.contacts.InputPhoneContact(
                client_id=i,
                phone=c["phone"],
                first_name=c["first_name"],
                last_name=c.get("last_name", ""),
            )
            for i, c in enumerate(contacts)
        ]
        result = await client(ImportContactsRequest(contacts=input_contacts))
        return f"Imported {len(result.imported)} contacts."
    except Exception as e:
        return log_and_format_error("import_contacts", e, contacts=contacts)


@mcp.tool()
async def export_contacts() -> str:
    """
    Export all contacts as a JSON string.
    """
    try:
        result = await client(GetContactsRequest(hash=0))
        users = result.users
        return json.dumps([format_entity(u) for u in users], indent=2)
    except Exception as e:
        return log_and_format_error("export_contacts", e)


@mcp.tool()
async def get_blocked_users() -> str:
    """
    Get a list of blocked users.
    """
    try:
        result = await client(functions.contacts.GetBlockedRequest(offset=0, limit=100))
        return json.dumps([format_entity(u) for u in result.users], indent=2)
    except Exception as e:
        return log_and_format_error("get_blocked_users", e)


@mcp.tool()
async def resolve_username(username: str) -> str:
    """
    Resolve a username to a user or chat ID.
    """
    try:
        result = await client(ResolveUsernameRequest(username=username))
        return str(result)
    except Exception as e:
        return log_and_format_error("resolve_username", e, username=username)


@mcp.tool()
async def search_public_chats(query: str) -> str:
    """
    Search for public chats, channels, or bots by username or title.
    """
    try:
        result = await client(functions.contacts.SearchRequest(q=query, limit=20))
        return json.dumps([format_entity(u) for u in result.users], indent=2)
    except Exception as e:
        return log_and_format_error("search_public_chats", e, query=query)
