"""
Message-related tool functions for Telegram MCP.

Functions for getting, sending, editing, and managing messages.
"""

from datetime import datetime, timedelta
from telethon import functions
from telethon.tl.types import User, Chat, Channel

from ..client import client, mcp
from ..utils import log_and_format_error

__all__ = [
    'get_messages',
    'list_messages',
    'get_message_context',
    'send_message',
    'forward_message',
    'edit_message',
    'delete_message',
    'pin_message',
    'unpin_message',
    'mark_as_read',
    'reply_to_message',
    'search_messages',
    'get_pinned_messages',
    'get_history'
]

@mcp.tool()
async def get_messages(chat_id: int, page: int = 1, page_size: int = 20) -> str:
    """
    Get paginated messages from a specific chat.
    Args:
        chat_id: The ID of the chat.
        page: Page number (1-indexed).
        page_size: Number of messages per page.
    """
    try:
        entity = await client.get_entity(chat_id)
        offset = (page - 1) * page_size
        messages = await client.get_messages(entity, limit=page_size, add_offset=offset)
        if not messages:
            return "No messages found for this page."
        lines = []
        for msg in messages:
            lines.append(f"ID: {msg.id} | Date: {msg.date} | Message: {msg.message}")
        return "\n".join(lines)
    except Exception as e:
        return log_and_format_error(
            "get_messages", e, chat_id=chat_id, page=page, page_size=page_size
        )


@mcp.tool()
async def list_messages(
    chat_id: int,
    limit: int = 20,
    search_query: str = None,
    from_date: str = None,
    to_date: str = None,
) -> str:
    """
    Retrieve messages with optional filters.

    Args:
        chat_id: The ID of the chat to get messages from.
        limit: Maximum number of messages to retrieve.
        search_query: Filter messages containing this text.
        from_date: Filter messages starting from this date (format: YYYY-MM-DD).
        to_date: Filter messages until this date (format: YYYY-MM-DD).
    """
    try:
        entity = await client.get_entity(chat_id)

        # Parse date filters if provided
        from_date_obj = None
        to_date_obj = None

        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
                # Make it timezone aware by adding UTC timezone info
                # Use datetime.timezone.utc for Python 3.9+ or import timezone directly for 3.13+
                try:
                    # For Python 3.9+
                    from_date_obj = from_date_obj.replace(tzinfo=datetime.timezone.utc)
                except AttributeError:
                    # For Python 3.13+
                    from datetime import timezone
                    from_date_obj = from_date_obj.replace(tzinfo=timezone.utc)
            except ValueError:
                return f"Invalid from_date format. Use YYYY-MM-DD."

        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
                # Set to end of day and make timezone aware
                to_date_obj = to_date_obj + timedelta(days=1, microseconds=-1)
                # Add timezone info
                try:
                    to_date_obj = to_date_obj.replace(tzinfo=datetime.timezone.utc)
                except AttributeError:
                    from datetime import timezone
                    to_date_obj = to_date_obj.replace(tzinfo=timezone.utc)
            except ValueError:
                return f"Invalid to_date format. Use YYYY-MM-DD."

        # Prepare filter parameters
        params = {}
        if search_query:
            params["search"] = search_query

        messages = await client.get_messages(entity, limit=limit, **params)

        # Apply date filters (Telethon doesn't support date filtering in get_messages directly)
        if from_date_obj or to_date_obj:
            filtered_messages = []
            for msg in messages:
                if from_date_obj and msg.date < from_date_obj:
                    continue
                if to_date_obj and msg.date > to_date_obj:
                    continue
                filtered_messages.append(msg)
            messages = filtered_messages

        if not messages:
            return "No messages found matching the criteria."

        lines = []
        for msg in messages:
            sender = ""
            if msg.sender:
                sender_name = getattr(msg.sender, "first_name", "") or getattr(
                    msg.sender, "title", "Unknown"
                )
                sender = f"{sender_name} | "

            lines.append(
                f"ID: {msg.id} | {sender}Date: {msg.date} | Message: {msg.message or '[Media/No text]'}"
            )

        return "\n".join(lines)
    except Exception as e:
        return log_and_format_error("list_messages", e, chat_id=chat_id)


@mcp.tool()
async def get_message_context(chat_id: int, message_id: int, context_size: int = 3) -> str:
    """
    Retrieve context around a specific message.

    Args:
        chat_id: The ID of the chat.
        message_id: The ID of the central message.
        context_size: Number of messages before and after to include.
    """
    try:
        chat = await client.get_entity(chat_id)
        # Get messages around the specified message
        messages_before = await client.get_messages(chat, limit=context_size, max_id=message_id)
        central_message = await client.get_messages(chat, ids=message_id)
        # Fix: get_messages(ids=...) returns a single Message, not a list
        if central_message is not None and not isinstance(central_message, list):
            central_message = [central_message]
        elif central_message is None:
            central_message = []
        messages_after = await client.get_messages(
            chat, limit=context_size, min_id=message_id, reverse=True
        )
        if not central_message:
            return f"Message with ID {message_id} not found in chat {chat_id}."
        # Combine messages in chronological order
        all_messages = list(messages_before) + list(central_message) + list(messages_after)
        all_messages.sort(key=lambda m: m.id)
        results = [f"Context for message {message_id} in chat {chat_id}:"]
        for msg in all_messages:
            sender_name = "Unknown"
            if msg.sender:
                sender_name = getattr(msg.sender, "first_name", "") or getattr(
                    msg.sender, "title", "Unknown"
                )
            highlight = " [THIS MESSAGE]" if msg.id == message_id else ""
            results.append(
                f"ID: {msg.id} | {sender_name} | {msg.date}{highlight}\n{msg.message or '[Media/No text]'}\n"
            )
        return "\n".join(results)
    except Exception as e:
        return log_and_format_error(
            "get_message_context",
            e,
            chat_id=chat_id,
            message_id=message_id,
            context_size=context_size,
        )


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
async def forward_message(from_chat_id: int, message_id: int, to_chat_id: int) -> str:
    """
    Forward a message from one chat to another.
    """
    try:
        from_entity = await client.get_entity(from_chat_id)
        to_entity = await client.get_entity(to_chat_id)
        await client.forward_messages(to_entity, message_id, from_entity)
        return f"Message {message_id} forwarded from {from_chat_id} to {to_chat_id}."
    except Exception as e:
        return log_and_format_error(
            "forward_message",
            e,
            from_chat_id=from_chat_id,
            message_id=message_id,
            to_chat_id=to_chat_id,
        )


@mcp.tool()
async def edit_message(chat_id: int, message_id: int, new_text: str) -> str:
    """
    Edit a message you sent.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.edit_message(entity, message_id, new_text)
        return f"Message {message_id} edited."
    except Exception as e:
        return log_and_format_error(
            "edit_message", e, chat_id=chat_id, message_id=message_id, new_text=new_text
        )


@mcp.tool()
async def delete_message(chat_id: int, message_id: int) -> str:
    """
    Delete a message by ID.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.delete_messages(entity, message_id)
        return f"Message {message_id} deleted."
    except Exception as e:
        return log_and_format_error("delete_message", e, chat_id=chat_id, message_id=message_id)


@mcp.tool()
async def pin_message(chat_id: int, message_id: int) -> str:
    """
    Pin a message in a chat.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.pin_message(entity, message_id)
        return f"Message {message_id} pinned in chat {chat_id}."
    except Exception as e:
        return log_and_format_error("pin_message", e, chat_id=chat_id, message_id=message_id)


@mcp.tool()
async def unpin_message(chat_id: int, message_id: int) -> str:
    """
    Unpin a message in a chat.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.unpin_message(entity, message_id)
        return f"Message {message_id} unpinned in chat {chat_id}."
    except Exception as e:
        return log_and_format_error("unpin_message", e, chat_id=chat_id, message_id=message_id)


@mcp.tool()
async def mark_as_read(chat_id: int) -> str:
    """
    Mark all messages as read in a chat.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.send_read_acknowledge(entity)
        return f"Marked all messages as read in chat {chat_id}."
    except Exception as e:
        return log_and_format_error("mark_as_read", e, chat_id=chat_id)


@mcp.tool()
async def reply_to_message(chat_id: int, message_id: int, text: str) -> str:
    """
    Reply to a specific message in a chat.
    """
    try:
        entity = await client.get_entity(chat_id)
        await client.send_message(entity, text, reply_to=message_id)
        return f"Replied to message {message_id} in chat {chat_id}."
    except Exception as e:
        return log_and_format_error(
            "reply_to_message", e, chat_id=chat_id, message_id=message_id, text=text
        )


@mcp.tool()
async def search_messages(chat_id: int, query: str, limit: int = 20) -> str:
    """
    Search for messages in a chat by text.
    """
    try:
        entity = await client.get_entity(chat_id)
        messages = await client.get_messages(entity, limit=limit, search=query)
        return "\n".join([f"ID: {m.id} | {m.date} | {m.message}" for m in messages])
    except Exception as e:
        return log_and_format_error(
            "search_messages", e, chat_id=chat_id, query=query, limit=limit
        )


@mcp.tool()
async def get_pinned_messages(chat_id: int) -> str:
    """
    Get all pinned messages in a chat.
    """
    try:
        entity = await client.get_entity(chat_id)
        # Use correct filter based on Telethon version
        try:
            # Try newer Telethon approach
            from telethon.tl.types import InputMessagesFilterPinned

            messages = await client.get_messages(entity, filter=InputMessagesFilterPinned())
        except (ImportError, AttributeError):
            # Fallback - try without filter and manually filter pinned
            all_messages = await client.get_messages(entity, limit=50)
            messages = [m for m in all_messages if getattr(m, "pinned", False)]

        if not messages:
            return "No pinned messages found in this chat."

        return "\n".join(
            [f"ID: {m.id} | {m.date} | {m.message or '[Media/No text]'}" for m in messages]
        )
    except Exception as e:
        return log_and_format_error("get_pinned_messages", e, chat_id=chat_id)


@mcp.tool()
async def get_history(chat_id: int, limit: int = 100) -> str:
    """
    Get full chat history (up to limit).
    """
    try:
        entity = await client.get_entity(chat_id)
        messages = await client.get_messages(entity, limit=limit)
        return "\n".join([f"ID: {m.id} | {m.date} | {m.message}" for m in messages])
    except Exception as e:
        return log_and_format_error("get_history", e, chat_id=chat_id, limit=limit)
