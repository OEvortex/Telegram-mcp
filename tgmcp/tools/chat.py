"""
Chat-related tool functions for Telegram MCP.

Functions for listing, getting, and managing chats.
"""

import json
from datetime import datetime, timedelta
from telethon import functions
from telethon.tl.types import User, Chat, Channel

from ..client import client, mcp
from ..utils import log_and_format_error, format_entity

__all__ = [
    'get_chats', 
    'list_chats', 
    'get_chat', 
    'get_direct_chat_by_contact',
    'send_message',
    'archive_chat',
    'unarchive_chat',
    'mute_chat',
    'unmute_chat',
    'get_invite_link',
    'export_chat_invite',
    'join_chat_by_link',
    'import_chat_invite'
]

@mcp.tool()
async def get_chats(page: int = 1, page_size: int = 20) -> str:
    """
    Get a paginated list of chats.
    Args:
        page: Page number (1-indexed).
        page_size: Number of chats per page.
    """
    try:
        dialogs = await client.get_dialogs()
        start = (page - 1) * page_size
        end = start + page_size
        if start >= len(dialogs):
            return "Page out of range."
        chats = dialogs[start:end]
        lines = []
        for dialog in chats:
            entity = dialog.entity
            chat_id = entity.id
            title = getattr(entity, "title", None) or getattr(entity, "first_name", "Unknown")
            lines.append(f"Chat ID: {chat_id}, Title: {title}")
        return "\n".join(lines)
    except Exception as e:
        return log_and_format_error("get_chats", e)


@mcp.tool()
async def list_chats(chat_type: str = None, limit: int = 20) -> str:
    """
    List available chats with metadata.

    Args:
        chat_type: Filter by chat type ('user', 'group', 'channel', or None for all)
        limit: Maximum number of chats to retrieve.
    """
    try:
        dialogs = await client.get_dialogs(limit=limit)

        results = []
        for dialog in dialogs:
            entity = dialog.entity

            # Filter by type if requested
            current_type = None
            if isinstance(entity, User):
                current_type = "user"
            elif isinstance(entity, Chat):
                current_type = "group"
            elif isinstance(entity, Channel):
                if getattr(entity, "broadcast", False):
                    current_type = "channel"
                else:
                    current_type = "group"  # Supergroup

            if chat_type and current_type != chat_type.lower():
                continue

            # Format chat info
            chat_info = f"Chat ID: {entity.id}"

            if hasattr(entity, "title"):
                chat_info += f", Title: {entity.title}"
            elif hasattr(entity, "first_name"):
                name = f"{entity.first_name}"
                if hasattr(entity, "last_name") and entity.last_name:
                    name += f" {entity.last_name}"
                chat_info += f", Name: {name}"

            chat_info += f", Type: {current_type}"

            if hasattr(entity, "username") and entity.username:
                chat_info += f", Username: @{entity.username}"

            # Add unread count if available
            if hasattr(dialog, "unread_count") and dialog.unread_count > 0:
                chat_info += f", Unread: {dialog.unread_count}"

            results.append(chat_info)

        if not results:
            return f"No chats found matching the criteria."

        return "\n".join(results)
    except Exception as e:
        return log_and_format_error("list_chats", e, chat_type=chat_type, limit=limit)


@mcp.tool()
async def get_chat(chat_id: int) -> str:
    """
    Get detailed information about a specific chat.

    Args:
        chat_id: The ID of the chat.
    """
    try:
        entity = await client.get_entity(chat_id)

        result = []
        result.append(f"ID: {entity.id}")

        is_channel = isinstance(entity, Channel)
        is_chat = isinstance(entity, Chat)
        is_user = isinstance(entity, User)

        if hasattr(entity, "title"):
            result.append(f"Title: {entity.title}")
            chat_type = (
                "Channel" if is_channel and getattr(entity, "broadcast", False) else "Group"
            )
            if is_channel and getattr(entity, "megagroup", False):
                chat_type = "Supergroup"
            elif is_chat:
                chat_type = "Group (Basic)"
            result.append(f"Type: {chat_type}")
            if hasattr(entity, "username") and entity.username:
                result.append(f"Username: @{entity.username}")

            # Fetch participants count reliably
            try:
                participants_count = (await client.get_participants(entity, limit=0)).total
                result.append(f"Participants: {participants_count}")
            except Exception as pe:
                result.append(f"Participants: Error fetching ({pe})")

        elif is_user:
            name = f"{entity.first_name}"
            if entity.last_name:
                name += f" {entity.last_name}"
            result.append(f"Name: {name}")
            result.append(f"Type: User")
            if entity.username:
                result.append(f"Username: @{entity.username}")
            if entity.phone:
                result.append(f"Phone: {entity.phone}")
            result.append(f"Bot: {'Yes' if entity.bot else 'No'}")
            result.append(f"Verified: {'Yes' if entity.verified else 'No'}")

        # Get last activity if it's a dialog
        try:
            # Using get_dialogs might be slow if there are many dialogs
            # Alternative: Get entity again via get_dialogs if needed for unread count
            dialog = await client.get_dialogs(limit=1, offset_id=0, offset_peer=entity)
            if dialog:
                dialog = dialog[0]
                result.append(f"Unread Messages: {dialog.unread_count}")
                if dialog.message:
                    last_msg = dialog.message
                    sender_name = "Unknown"
                    if last_msg.sender:
                        sender_name = getattr(last_msg.sender, "first_name", "") or getattr(
                            last_msg.sender, "title", "Unknown"
                        )
                        if hasattr(last_msg.sender, "last_name") and last_msg.sender.last_name:
                            sender_name += f" {last_msg.sender.last_name}"
                    sender_name = sender_name.strip() or "Unknown"
                    result.append(f"Last Message: From {sender_name} at {last_msg.date}")
                    result.append(f"Message: {last_msg.message or '[Media/No text]'}")
        except Exception as diag_ex:
            pass

        return "\n".join(result)
    except Exception as e:
        return log_and_format_error("get_chat", e, chat_id=chat_id)


@mcp.tool()
async def get_direct_chat_by_contact(contact_query: str) -> str:
    """
    Find a direct chat with a specific contact by name, username, or phone.

    Args:
        contact_query: Name, username, or phone number to search for.
    """
    try:
        # Fetch all contacts using the correct Telethon method
        result = await client(functions.contacts.GetContactsRequest(hash=0))
        contacts = result.users
        found_contacts = []
        for contact in contacts:
            if not contact:
                continue
            name = (
                f"{getattr(contact, 'first_name', '')} {getattr(contact, 'last_name', '')}".strip()
            )
            username = getattr(contact, "username", "")
            phone = getattr(contact, "phone", "")
            if (
                contact_query.lower() in name.lower()
                or (username and contact_query.lower() in username.lower())
                or (phone and contact_query in phone)
            ):
                found_contacts.append(contact)
        if not found_contacts:
            return f"No contacts found matching '{contact_query}'."
        # If we found contacts, look for direct chats with them
        results = []
        dialogs = await client.get_dialogs()
        for contact in found_contacts:
            contact_name = (
                f"{getattr(contact, 'first_name', '')} {getattr(contact, 'last_name', '')}".strip()
            )
            for dialog in dialogs:
                if isinstance(dialog.entity, User) and dialog.entity.id == contact.id:
                    chat_info = f"Chat ID: {dialog.entity.id}, Contact: {contact_name}"
                    if getattr(contact, "username", ""):
                        chat_info += f", Username: @{contact.username}"
                    if dialog.unread_count:
                        chat_info += f", Unread: {dialog.unread_count}"
                    results.append(chat_info)
                    break
        if not results:
            found_names = ", ".join(
                [f"{c.first_name} {c.last_name}".strip() for c in found_contacts]
            )
            return f"Found contacts: {found_names}, but no direct chats were found with them."
        return "\n".join(results)
    except Exception as e:
        return log_and_format_error("get_direct_chat_by_contact", e, contact_query=contact_query)


@mcp.tool()
async def send_message(chat_id: int, message: str) -> str:
    """
    Send a message to a specific chat.
    Args:
        chat_id: The ID of the chat.
        message: The message content to send.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.send_message(entity, message)
        return "Message sent successfully."
    except Exception as e:
        return log_and_format_error("send_message", e, chat_id=chat_id)


@mcp.tool()
async def archive_chat(chat_id: int) -> str:
    """
    Archive a chat.
    """
    try:
        await client(
            functions.messages.ToggleDialogPinRequest(
                peer=await client.get_entity(chat_id), pinned=True
            )
        )
        return f"Chat {chat_id} archived."
    except Exception as e:
        return log_and_format_error("archive_chat", e, chat_id=chat_id)


@mcp.tool()
async def unarchive_chat(chat_id: int) -> str:
    """
    Unarchive a chat.
    """
    try:
        await client(
            functions.messages.ToggleDialogPinRequest(
                peer=await client.get_entity(chat_id), pinned=False
            )
        )
        return f"Chat {chat_id} unarchived."
    except Exception as e:
        return log_and_format_error("unarchive_chat", e, chat_id=chat_id)


@mcp.tool()
async def mute_chat(chat_id: int) -> str:
    """
    Mute notifications for a chat.
    """
    try:
        from telethon.tl.types import InputPeerNotifySettings

        peer = await client.get_entity(chat_id)
        await client(
            functions.account.UpdateNotifySettingsRequest(
                peer=peer, settings=InputPeerNotifySettings(mute_until=2**31 - 1)
            )
        )
        return f"Chat {chat_id} muted."
    except (ImportError, AttributeError) as type_err:
        try:
            # Alternative approach directly using raw API
            peer = await client.get_input_entity(chat_id)
            await client(
                functions.account.UpdateNotifySettingsRequest(
                    peer=peer,
                    settings={
                        "mute_until": 2**31 - 1,  # Far future
                        "show_previews": False,
                        "silent": True,
                    },
                )
            )
            return f"Chat {chat_id} muted (using alternative method)."
        except Exception as alt_e:
            return log_and_format_error("mute_chat", alt_e, chat_id=chat_id)
    except Exception as e:
        return log_and_format_error("mute_chat", e, chat_id=chat_id)


@mcp.tool()
async def unmute_chat(chat_id: int) -> str:
    """
    Unmute notifications for a chat.
    """
    try:
        from telethon.tl.types import InputPeerNotifySettings

        peer = await client.get_entity(chat_id)
        await client(
            functions.account.UpdateNotifySettingsRequest(
                peer=peer, settings=InputPeerNotifySettings(mute_until=0)
            )
        )
        return f"Chat {chat_id} unmuted."
    except (ImportError, AttributeError) as type_err:
        try:
            # Alternative approach directly using raw API
            peer = await client.get_input_entity(chat_id)
            await client(
                functions.account.UpdateNotifySettingsRequest(
                    peer=peer,
                    settings={
                        "mute_until": 0,  # Unmute (current time)
                        "show_previews": True,
                        "silent": False,
                    },
                )
            )
            return f"Chat {chat_id} unmuted (using alternative method)."
        except Exception as alt_e:
            return log_and_format_error("unmute_chat", alt_e, chat_id=chat_id)
    except Exception as e:
        return log_and_format_error("unmute_chat", e, chat_id=chat_id)


@mcp.tool()
async def get_invite_link(chat_id: int) -> str:
    """
    Get the invite link for a group or channel.
    """
    try:
        entity = await client.get_entity(chat_id)

        # Try using ExportChatInviteRequest first
        try:
            from telethon.tl import functions

            result = await client(functions.messages.ExportChatInviteRequest(peer=entity))
            return result.link
        except AttributeError:
            # If the function doesn't exist in the current Telethon version
            pass
        except Exception as e1:
            # If that fails, log and try alternative approach
            pass

        # Alternative approach using client.export_chat_invite_link
        try:
            invite_link = await client.export_chat_invite_link(entity)
            return invite_link
        except Exception as e2:
            pass

        # Last resort: Try directly fetching chat info
        try:
            if isinstance(entity, (Chat, Channel)):
                full_chat = await client(functions.messages.GetFullChatRequest(chat_id=entity.id))
                if hasattr(full_chat, "full_chat") and hasattr(full_chat.full_chat, "invite_link"):
                    return full_chat.full_chat.invite_link or "No invite link available."
        except Exception as e3:
            pass

        return "Could not retrieve invite link for this chat."
    except Exception as e:
        return log_and_format_error("get_invite_link", e, chat_id=chat_id)


@mcp.tool()
async def export_chat_invite(chat_id: int) -> str:
    """
    Export a chat invite link.
    """
    try:
        entity = await client.get_entity(chat_id)

        # Try using ExportChatInviteRequest first
        try:
            from telethon.tl import functions

            result = await client(functions.messages.ExportChatInviteRequest(peer=entity))
            return result.link
        except AttributeError:
            # If the function doesn't exist in the current Telethon version
            pass
        except Exception as e1:
            # If that fails, log and try alternative approach
            pass

        # Alternative approach using client.export_chat_invite_link
        try:
            invite_link = await client.export_chat_invite_link(entity)
            return invite_link
        except Exception as e2:
            return log_and_format_error("export_chat_invite", e2, chat_id=chat_id)
    except Exception as e:
        return log_and_format_error("export_chat_invite", e, chat_id=chat_id)


@mcp.tool()
async def join_chat_by_link(link: str) -> str:
    """
    Join a chat by invite link.
    """
    try:
        # Extract the hash from the invite link
        if "/" in link:
            hash_part = link.split("/")[-1]
            if hash_part.startswith("+"):
                hash_part = hash_part[1:]  # Remove the '+' if present
        else:
            hash_part = link

        # Try checking the invite before joining
        try:
            from telethon.errors import (
                InviteHashExpiredError,
                InviteHashInvalidError,
                UserAlreadyParticipantError,
                ChatAdminRequiredError,
                UsersTooMuchError,
            )

            # Try to check invite info first (will often fail if not a member)
            invite_info = await client(functions.messages.CheckChatInviteRequest(hash=hash_part))
            if hasattr(invite_info, "chat") and invite_info.chat:
                # If we got chat info, we're already a member
                chat_title = getattr(invite_info.chat, "title", "Unknown Chat")
                return f"You are already a member of this chat: {chat_title}"
        except Exception as check_err:
            # This often fails if not a member - just continue
            pass

        # Join the chat using the hash
        try:
            result = await client(functions.messages.ImportChatInviteRequest(hash=hash_part))
            if result and hasattr(result, "chats") and result.chats:
                chat_title = getattr(result.chats[0], "title", "Unknown Chat")
                return f"Successfully joined chat: {chat_title}"
            return f"Joined chat via invite hash."
        except Exception as join_err:
            err_str = str(join_err).lower()
            if "expired" in err_str:
                return "The invite hash has expired and is no longer valid."
            elif "invalid" in err_str:
                return "The invite hash is invalid or malformed."
            elif "already" in err_str and "participant" in err_str:
                return "You are already a member of this chat."
            elif "admin" in err_str:
                return "Cannot join this chat - requires admin approval."
            elif "too much" in err_str or "too many" in err_str:
                return "Cannot join this chat - it has reached maximum number of participants."
            else:
                raise  # Re-raise to be caught by the outer exception handler
    except Exception as e:
        return log_and_format_error("join_chat_by_link", e, link=link)


@mcp.tool()
async def import_chat_invite(hash: str) -> str:
    """
    Import a chat invite by hash.
    """
    try:
        # Remove any prefixes like '+' if present
        if hash.startswith("+"):
            hash = hash[1:]

        # Try checking the invite before joining
        try:
            from telethon.errors import (
                InviteHashExpiredError,
                InviteHashInvalidError,
                UserAlreadyParticipantError,
                ChatAdminRequiredError,
                UsersTooMuchError,
            )

            # Try to check invite info first (will often fail if not a member)
            invite_info = await client(functions.messages.CheckChatInviteRequest(hash=hash))
            if hasattr(invite_info, "chat") and invite_info.chat:
                # If we got chat info, we're already a member
                chat_title = getattr(invite_info.chat, "title", "Unknown Chat")
                return f"You are already a member of this chat: {chat_title}"
        except Exception as check_err:
            # This often fails if not a member - just continue
            pass

        # Join the chat using the hash
        try:
            result = await client(functions.messages.ImportChatInviteRequest(hash=hash))
            if result and hasattr(result, "chats") and result.chats:
                chat_title = getattr(result.chats[0], "title", "Unknown Chat")
                return f"Successfully joined chat: {chat_title}"
            return f"Joined chat via invite hash."
        except Exception as join_err:
            err_str = str(join_err).lower()
            if "expired" in err_str:
                return "The invite hash has expired and is no longer valid."
            elif "invalid" in err_str:
                return "The invite hash is invalid or malformed."
            elif "already" in err_str and "participant" in err_str:
                return "You are already a member of this chat."
            elif "admin" in err_str:
                return "Cannot join this chat - requires admin approval."
            elif "too much" in err_str or "too many" in err_str:
                return "Cannot join this chat - it has reached maximum number of participants."
            else:
                raise  # Re-raise to be caught by the outer exception handler
    except Exception as e:
        return log_and_format_error("import_chat_invite", e, hash=hash)
